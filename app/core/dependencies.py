from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.parse import ParseService
from app.services.job import JobService
from app.repositories.advert import AdvertRepository
from app.repositories.job import JobRepository


def get_parse_service(session: AsyncSession = Depends(get_db)) -> ParseService:
    repo = AdvertRepository(session)
    return ParseService(repo)


def get_job_service(session: AsyncSession = Depends(get_db)) -> JobService:
    repo = JobRepository(session)
    return JobService(repo)
