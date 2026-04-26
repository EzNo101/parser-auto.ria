import logging
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisState:
    client: redis.Redis | None = None


state = RedisState()


async def init_redis() -> None:
    if not settings.REDIS_URL:
        logger.info("Redis URL is not set. Skipping redis init")
        return

    try:
        client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )

        await state.client.ping()  # type: ignore

        state.client = client
        logger.info("Redis connected")

    except Exception as e:
        logger.error(f"Redis connection failed {e}")


async def close_redis() -> None:
    if state.client is not None:
        await state.client.aclose()
        state.client = None
        logger.info("Redis connection closed.")


async def get_redis() -> redis.Redis:
    if state.client is None:
        raise RuntimeError("Redis not intialized")
    return state.client
