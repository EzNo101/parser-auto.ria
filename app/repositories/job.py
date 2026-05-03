from typing import Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.advert import JobAdvert


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[JobAdvert]:
        result = await self.session.execute(select(JobAdvert))
        return list(result.scalars().all())

    async def get_active(self) -> list[JobAdvert]:
        result = await self.session.execute(select(JobAdvert).where(JobAdvert.active))

        return list(result.scalars().all())

    async def get_due(self, now: datetime) -> list[JobAdvert]:
        result = await self.session.execute(
            select(JobAdvert).where(
                JobAdvert.active,
                JobAdvert.next_run_at.is_not(None),
                JobAdvert.next_run_at <= now,
            )
        )

        return list(result.scalars().all())

    async def get_by_id(self, job_id: int) -> JobAdvert | None:
        result = await self.session.execute(
            select(JobAdvert).where(JobAdvert.id == job_id)
        )

        return result.scalar_one_or_none()

    async def update(self, job: JobAdvert, updates: dict[str, Any]) -> JobAdvert:
        for field, value in updates.items():
            setattr(job, field, value)

        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def disable(self, job: JobAdvert) -> JobAdvert:
        job.active = False
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def delete(self, job: JobAdvert) -> None:
        await self.session.delete(job)
        await self.session.commit()

    async def create(
        self,
        url: str,
        max_pages: int,
        interval_hours: int,
        active: bool,
        last_run_at: datetime | None,
        next_run_at: datetime,
    ) -> JobAdvert:
        job = JobAdvert(
            url=url,
            max_pages=max_pages,
            interval_hours=interval_hours,
            active=active,
            last_run_at=last_run_at,
            next_run_at=next_run_at,
        )

        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)

        return job
