"""Redis asynchronous client wrapper with fallback capabilities."""

from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> Optional[aioredis.Redis]:
    """Initializes the async Redis connection pool."""
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2.0,
        )
        await redis_client.ping()
        logger.info("Successfully connected to Redis instance.")
        return redis_client
    except Exception as e:
        logger.warning(
            f"Redis is not available at {settings.REDIS_URL} ({str(e)}). Running in degraded mode without distributed cache."
        )
        redis_client = None
        return None


async def close_redis() -> None:
    """Closes the Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> Optional[aioredis.Redis]:
    """Dependency or service accessor for Redis."""
    return redis_client


async def is_token_blacklisted(token_jti: str) -> bool:
    """Checks if a revoked JWT ID is present in the blacklist."""
    if not redis_client:
        return False
    try:
        return bool(await redis_client.get(f"blacklist:{token_jti}"))
    except Exception:
        return False


async def blacklist_token(token_jti: str, expire_seconds: int) -> None:
    """Blacklists a revoked token until its natural expiration."""
    if not redis_client:
        return
    try:
        await redis_client.setex(f"blacklist:{token_jti}", expire_seconds, "revoked")
    except Exception as e:
        logger.error(f"Failed to blacklist token {token_jti}: {e}")
