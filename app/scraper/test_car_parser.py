import asyncio

import httpx
from fake_useragent import UserAgent

from car_page import CarPageParse


URL = "https://auto.ria.com/auto_tesla_model_s_39752802.html"


async def main() -> None:
    ua = UserAgent()

    async with httpx.AsyncClient(
        headers={
            "User-Agent": ua.random,
            "Accept": "*/*",
            "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        follow_redirects=True,
        timeout=30,
    ) as client:
        parser = CarPageParse()
        result = await parser.parse(URL, client)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
