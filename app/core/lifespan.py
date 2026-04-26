import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine
from app.db.redis import init_redis, close_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: init Redis")
    await init_redis()

    yield

    logger.info("Shutdown: dispose PostgreSQL")
    await engine.dispose()

    logger.info("Shutdown: close Redis")
    await close_redis()
