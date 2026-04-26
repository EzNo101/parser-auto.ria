from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.advert import Advert


class AdvertRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, ad_id: int) -> Advert | None:
        result = await self.session.execute(select(Advert).where(Advert.id == ad_id))
        return result.scalar_one_or_none()

    async def get_by_auto_id(self, auto_id: int) -> Advert | None:
        result = await self.session.execute(
            select(Advert).where(Advert.auto_id == auto_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, auto_id: str, url: str, title: str, phone_number: str
    ) -> Advert:
        parsed_advert = Advert(
            auto_id=auto_id,
            url=url,
            title=title,
            phone_number=phone_number,
        )

        self.session.add(parsed_advert)
        await self.session.commit()
        await self.session.refresh(parsed_advert)

        return parsed_advert

    async def delete_advert(self, advert: Advert) -> None:
        await self.session.delete(advert)
