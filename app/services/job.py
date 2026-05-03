from datetime import datetime, timezone, timedelta

from app.repositories.job import JobRepository
from app.models.advert import JobAdvert
from app.schemas.adverts import JobAdvertUpdate, JobAdvertCreate
from app.core.error import JobNotFoundError


class JobService:
    def __init__(self, repo: JobRepository):
        self.repo = repo

    async def get_all(self) -> list[JobAdvert]:
        result = await self.repo.get_all()
        if not result:
            raise JobNotFoundError("No jobs found")

        return result

    async def get_active(self) -> list[JobAdvert]:
        result = await self.repo.get_active()
        if not result:
            raise JobNotFoundError("No active jobs found")

        return result

    async def get_due(self) -> list[JobAdvert]:
        return await self.repo.get_due(datetime.now(timezone.utc))

    async def get_by_id(self, job_id: int) -> JobAdvert:
        job = await self.repo.get_by_id(job_id)
        if job is None:
            raise JobNotFoundError("Job not found")

        return job

    async def update(self, job_id: int, data: JobAdvertUpdate) -> JobAdvert:
        job = await self.get_by_id(job_id)

        updates = data.model_dump(exclude_none=True, exclude_unset=True)
        if not updates:
            return job

        updated_job = await self.repo.update(job, updates)
        return updated_job

    async def create(self, data: JobAdvertCreate) -> JobAdvert:
        job = await self.repo.create(
            url=data.url,
            max_pages=data.max_pages,
            interval_hours=data.interval_hours,
            active=data.active,
            last_run_at=None,
            next_run_at=datetime.now(timezone.utc)
            + timedelta(hours=data.interval_hours),
        )

        return job

    async def disable(self, job_id: int) -> JobAdvert:
        job = await self.get_by_id(job_id)
        return await self.repo.disable(job)

    async def delete(self, job_id: int) -> None:
        job = await self.get_by_id(job_id)
        await self.repo.delete(job)
