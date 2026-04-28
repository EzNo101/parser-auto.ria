from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class SearchPageParser:
    def __init__(self):
        self.base_url = "https://auto.ria.com"
        self.ua = UserAgent()

    def _get_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def _extract_car_links(self, soup: BeautifulSoup) -> list[str]:
        links: list[str] = []

        for tag in soup.select(
            'a[href*="/auto_"][href*=".html"]'
        ):  # find all <a> with /auto_..._id.html
            href = tag.get("href")
            if not isinstance(href, str):
                continue

            if href.startswith("/"):
                href = self.base_url + href
            links.append(href)

        return list(dict.fromkeys(links))  # remove duplicates

    def _get_page_url(self, url: str, page: int) -> str:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        query["page"] = [str(page)]
        new_query = urlencode(query, doseq=True)
        parts = list(parsed)
        parts[4] = new_query

        return urlunparse(parts)

    async def parse_adverts(
        self,
        start_url: str,
        client: httpx.AsyncClient,
        max_pages: int = 1,
    ):
        all_links: list[str] = []

        for page in range(max_pages):
            page_url = self._get_page_url(start_url, page)
            headers = {"User-Agent": self.ua.random}
            response = await client.get(page_url, headers=headers)
            if response.status_code != 200:
                continue

            soup = self._get_soup(response.text)
            links = self._extract_car_links(soup)
            if not links:
                break
            all_links.extend(links)

        return list(dict.fromkeys(all_links))
