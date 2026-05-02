import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    logger.info("Shutdown: dispose PostgreSQL")
    await engine.dispose()
