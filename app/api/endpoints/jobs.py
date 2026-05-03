from fastapi import APIRouter, HTTPException, status, Depends
from typing import Any, Dict

from app.services.job import JobService
from app.core.dependencies import get_job_service
from app.schemas.adverts import JobAdvertCreate, JobAdvertResponse, JobAdvertUpdate
from app.tasks.parse import run_parse
from app.core.error import JobNotFoundError

router = APIRouter(prefix="/jobs", tags=["celery-tasks", "jobs"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[JobAdvertResponse])
async def list_jobs(service: JobService = Depends(get_job_service)):
    try:
        return await service.get_all()
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=JobAdvertResponse)
async def create_job(
    payload: JobAdvertCreate, service: JobService = Depends(get_job_service)
):
    return await service.create(payload)


@router.patch(
    "/{job_id}", status_code=status.HTTP_200_OK, response_model=JobAdvertResponse
)
async def update_job(
    job_id: int,
    payload: JobAdvertUpdate,
    service: JobService = Depends(get_job_service),
):
    try:
        return await service.update(job_id, payload)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{job_id}/disable",
    status_code=status.HTTP_200_OK,
    response_model=JobAdvertResponse,
)
async def disable_job(job_id: int, service: JobService = Depends(get_job_service)):
    try:
        return await service.disable(job_id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{job_id}/run",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=Dict[str, Any],
)
async def run_job_now(
    job_id: int, service: JobService = Depends(get_job_service)
) -> Dict[str, Any]:
    try:
        job = await service.get_by_id(job_id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    run_parse.delay(job.url, job.max_pages)  # type: ignore[aqttr-defined]
    return {"status": "queued", "job_id": job_id}
