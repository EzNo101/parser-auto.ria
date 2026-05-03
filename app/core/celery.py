from celery import Celery  # type: ignore
from app.core.config import settings

celery_app = Celery(
    "parser",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BROKER_URL,
)


celery_app.conf.update(  # pyright: ignore[reportUnknownMemberType]
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Kyiv",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {  # pyright: ignore[reportUnknownMemberType]
    "run-due-jobs-every-5-min": {
        "task": "app.tasks.parse.run_due_jobs",
        "schedule": 300.0,
    },
}

celery_app.autodiscover_tasks(["app.tasks"])  # pyright: ignore[reportUnknownMemberType]
