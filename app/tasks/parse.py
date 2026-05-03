import asyncio
import logging
from typing import Any
from datetime import datetime, timezone, timedelta

from app.core.celery import celery_app
from app.db.session import AsyncSessionLocal
from app.services.parse import ParseService
from app.repositories.advert import AdvertRepository
from app.repositories.job import JobRepository
from app.services.job import JobService

logger = logging.getLogger(__name__)


async def _run_parse(url: str, max_pages: int) -> int:
    async with AsyncSessionLocal() as session:
        service = ParseService(AdvertRepository(session))
        adverts = await service.parse(url=url, max_pages=max_pages)
        return len(adverts)


@celery_app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def run_parse(url: str, max_pages: int = 1) -> dict[str, Any]:
    processed = asyncio.run(_run_parse(url, max_pages))

    return {
        "status": "success",
        "processed": processed,
        "url": url,
    }


async def _delete_all() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        service = ParseService(AdvertRepository(session))
        await service.delete_all()
        return {"status": "success"}


@celery_app.task
def delete_all() -> dict[str, str]:
    return asyncio.run(_delete_all())


async def _run_due_jobs() -> int:
    async with AsyncSessionLocal() as session:
        service = JobService(JobRepository(session))
        now = datetime.now(timezone.utc)
        jobs = await service.get_due()

        for job in jobs:
            run_parse.delay(job.url, job.max_pages)  # type: ignore[attr-defined]

            updates = {
                "last_run_at": now,
                "next_run_at": now + timedelta(hours=job.interval_hours),
            }
            await service.repo.update(job, updates)

        logger.info("run_due_jobs scheduled %s jobs", len(jobs))
        return len(jobs)


@celery_app.task
def run_due_jobs() -> int:
    return asyncio.run(_run_due_jobs())


# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUntypedFunctionDecorator=false
