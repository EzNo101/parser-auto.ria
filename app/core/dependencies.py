from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.parse import ParseService
from app.repositories.advert import AdvertRepository


def get_parse_service(session: AsyncSession = Depends(get_db)) -> ParseService:
    repo = AdvertRepository(session)
    return ParseService(repo)
