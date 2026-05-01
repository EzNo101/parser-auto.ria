import httpx
import csv
import io

from app.repositories.advert import AdvertRepository
from app.scraper.search_page import SearchPageParser
from app.scraper.car_page import CarPageParse
from app.models.advert import Advert
from app.scraper.car_page import Advert as AdvertDict
from app.core.error import AdvertNotFoundError, NoParsedAdverts


class ParseService:
    def __init__(self, repo: AdvertRepository):
        self.repo = repo

    async def get_all(self) -> list[Advert]:
        result = await self.repo.get_all()
        if not result:
            raise AdvertNotFoundError("No adverts found")
        return result

    async def get_by_id(self, advert_id: int) -> Advert:
        advert = await self.repo.get_by_id(advert_id)
        if advert is None:
            raise AdvertNotFoundError("Advert not found")
        return advert

    async def get_by_auto_id(self, auto_id: str) -> Advert:
        advert = await self.repo.get_by_auto_id(auto_id)
        if advert is None:
            raise AdvertNotFoundError("Advert not found")
        return advert

    async def get_by_number(self, phone_number: str) -> Advert:
        advert = await self.repo.get_by_phone_number(phone_number)
        if advert is None:
            raise AdvertNotFoundError("Advert not found")
        return advert

    async def parse(self, url: str, max_pages: int) -> list[AdvertDict]:
        search_pages_parser = SearchPageParser()
        car_pages_parser = CarPageParse()

        adverts: list[AdvertDict] = []
        async with httpx.AsyncClient() as client:
            links = await search_pages_parser.parse_adverts(
                url,
                client,
                max_pages,
            )
            for link in links:
                advert = await car_pages_parser.parse_car(link, client)
                if advert:
                    adverts.append(advert)

        if not adverts:
            raise NoParsedAdverts("No adverts parsed")

        for advert in adverts:
            await self.repo.create(
                auto_id=advert["auto_id"],
                url=advert["url"],
                title=advert["title"] or "",
                phone_number=advert["phone_number"],
            )

        return adverts

    async def create(
        self, auto_id: str, url: str, title: str, phone_number: str
    ) -> Advert:
        return await self.repo.create(
            auto_id=auto_id,
            url=url,
            title=title,
            phone_number=phone_number,
        )

    async def delete_advert(self, advert_id: int) -> None:
        advert = await self.repo.get_by_id(advert_id)
        if advert is None:
            raise AdvertNotFoundError("Advert not found")
        await self.repo.delete_advert(advert)

    async def delete_all(self) -> None:
        adverts = await self.repo.get_all()
        for advert in adverts:
            await self.repo.delete_advert(advert)

    def build_vcard(self, title: str, phone_number: str, url: str) -> str:
        title = title.replace("\n", " ").strip()
        phone_number = phone_number.strip()
        url = url.replace("\n", " ").strip()

        return (
            "BEGIN:VCARD\n"
            "VERSION:3.0\n"
            f"N:;{title};;;\n"
            f"FN:{title}\n"
            f"TEL;TYPE=CELL:{phone_number}\n"
            f"URL:{url}\n"
            "END:VCARD\n"
        )

    def build_csv(self, title: str, phone_number: str, url: str) -> str:
        title = title.replace("\n", " ").strip()
        phone_number = phone_number.strip()
        url = url.replace("\n", " ").strip()

        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow([title, phone_number, url])
        return buffer.getvalue()

    async def stream_all(self):
        stream = self.repo.stream_all()
        first = await anext(stream, None)
        if first is None:
            raise AdvertNotFoundError("No adverts found")

        async def gen():
            yield first
            async for advert in stream:
                yield advert

        return gen()
