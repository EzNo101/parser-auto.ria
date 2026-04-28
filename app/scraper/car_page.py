from typing import Any, TypedDict
import re
import json
import httpx
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class Advert(TypedDict):
    auto_id: str
    url: str
    title: str
    phone_number: str


class CarPageParse:
    def _get_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def _extract_auto_id(self, url: str) -> str:
        match = re.search(r"/auto_[^/]+_(\d+)\.html", url)
        return match.group(1) if match else ""  # only id

    def _extract_action_data(self, html_text: str) -> dict[str, Any] | None:
        """
        Extract actionData JSON block from the HTML.

        AutoRia does not include the phone number directly in the HTML.
        Instead, it stores a JSON object (actionData) that is later used
        to make a POST request to get the phone number.

        This function finds and extracts that JSON block.
        """

        # Find the "Show phone" button block.
        marker = '"id":"autoPhone"'

        # Get position of that block in HTML.
        index = html_text.find(marker)

        # If not found, no phone popup data is available.
        if index == -1:
            return None

        # Find "actionData" JSON near the phone button.
        action_index = html_text.find('"actionData":', index)

        # If not found, we cannot build the phone request payload.
        if action_index == -1:
            return None

        # Find the first "{" after "actionData" — this is the JSON start.
        start = html_text.find("{", action_index)

        # Safety check: if no JSON start found, stop.
        if start == -1:
            return None

        # Tracks how many JSON object levels are open.
        depth = 0

        # True when we are inside a string like "...".
        in_string = False

        # True when the previous character was a backslash "\".
        escape = False

        # Walk through the HTML text character by character,
        # starting from the JSON opening brace.
        for i in range(start, len(html_text)):
            char = html_text[i]

            # If previous char was "\", skip this character.
            if escape:
                escape = False
                continue

            # If current char is "\", the next char is escaped.
            if char == "\\":
                escape = True
                continue

            # If current char is a quote, enter or exit string mode.
            if char == '"':
                in_string = not in_string
                continue

            # Ignore all characters inside JSON strings.
            if in_string:
                continue

            # Found opening brace: one JSON level deeper.
            if char == "{":
                depth += 1

            # Found closing brace: one JSON level closed.
            elif char == "}":
                depth -= 1

                # If depth is 0, the full JSON object is captured.
                if depth == 0:
                    raw_json = html_text[start : i + 1]
                    return json.loads(raw_json)

        # If loop finished and JSON was not closed properly.
        return None

    def _find_phone(self, obj: Any) -> str | None:
        if isinstance(obj, dict):
            for key, value in obj.items():  # pyright: ignore[reportUnknownVariableType]
                key_text = str(key)  # pyright: ignore[reportUnknownArgumentType]

                if isinstance(value, str):
                    if value.startswith("tel:"):
                        return value.replace("tel:", "").strip()

                    if "phone" in key_text.lower() and re.search(r"\d{7,}", value):
                        return value

                result = self._find_phone(value)
                if result:
                    return result

        elif isinstance(obj, list):
            for item in obj:  # pyright: ignore[reportUnknownVariableType]
                result = self._find_phone(item)
                if result:
                    return result

        return None

    async def _fetch_phone(
        self, html_text: str, url: str, client: httpx.AsyncClient
    ) -> str | None:

        action_data = self._extract_action_data(html_text)
        if not action_data:
            print("action data not found")
            return None

        auto_id = self._extract_auto_id(url)
        if not auto_id:
            print("auto id not found")
            return None

        data = action_data.get("data", [])

        # convert list -> dict
        params = {}
        for item in data:
            if isinstance(item, list) and len(item) == 2:  # type: ignore
                params[item[0]] = item[1]

        payload: dict[str, Any] = {
            "blockId": "autoPhone",
            "popUpId": "autoPhone",
            "autoId": int(auto_id),
            "target": {},
            "langId": 4,
            "device": "desktop-web",
            "isLoginRequired": False,
            "isConfirmPhoneEmailRequired": False,
            "formId": None,
            "data": data,
            "params": params,
        }

        headers = {
            "User-Agent": UserAgent().random,
            "Content-Type": "application/json",
            "Origin": "https://auto.ria.com",
            "Referer": url,
            "x-ria-source": "vue3-1.72.1",
        }

        response = await client.post(
            "https://auto.ria.com/bff/final-page/public/auto/popUp/",
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            print("Phone request failed!", response.status_code)
            return None

        json_data = response.json()

        return self._find_phone(json_data)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        if soup.title:
            title = soup.title.get_text(strip=True)

            title = title.replace("AUTO.RIA – Продам ", "")

            if "," in title:
                title = title.split(",")[0]

            return title.strip()
        return ""

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"[^\d]", "", phone)

        if digits.startswith("0") and len(digits) >= 10:
            return "+380" + digits[1:]

        if digits.startswith("380"):
            return "+" + digits

        return "+" + digits

    async def parse_car(self, url: str, client: httpx.AsyncClient) -> Advert | None:
        response = await client.get(url)

        if response.status_code != 200:
            return None

        html = response.text
        soup = self._get_soup(html)

        final_url = str(response.url)
        auto_id = self._extract_auto_id(final_url) or self._extract_auto_id(url)

        if not auto_id:
            return None

        phone = await self._fetch_phone(html, final_url, client)

        return Advert(
            auto_id=auto_id,
            url=url,
            title=self._extract_title(soup),
            phone_number=self._normalize_phone(phone) if phone else "",
        )

        # return {
        #     "auto_id": auto_id,
        #     "url": final_url,
        #     "title": self._extract_title(soup),
        #     "phone_number": self._normalize_phone(phone) if phone else None,
        # }
