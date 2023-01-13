import logging

from datetime import datetime, timedelta

from redis.asyncio import Redis

from dm_stream_urls_server.config import CACHE_HOST

logger = logging.getLogger(__name__)

Cache = Redis

CACHE_KEY = "dailymotion_api_access_token"
LOCK_KEY = f"{CACHE_KEY}_cached"


def get_cache() -> Cache | None:
    """Return a connection to the cache server"""

    try:
        return Redis.from_url(f"redis://{CACHE_HOST}/")
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.error(
            "Failed to connect to cache: "
            "CACHE_HOST=%s, exception_type=%s, exception_message=%s",
            CACHE_HOST,
            exception_type,
            exception_message,
        )

        return None


async def is_access_token_expired(cache: Cache) -> bool:
    """Check whether the access token cache has expired"""

    try:
        return not bool(await cache.get(LOCK_KEY))
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.warning(
            "Failed to get dailymotion access token lock: "
            "exception_type=%s, exception_message=%s",
            exception_type,
            exception_message,
        )

        return True


async def read_access_token(cache: Cache) -> str | None:
    """Read access token from cache"""

    try:
        if cached_access_token := await cache.get(CACHE_KEY):
            access_token: str = cached_access_token.decode("utf8")

            return access_token
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.warning(
            "Failed to get dailymotion access token from cache: "
            "exception_type=%s, exception_message=%s",
            exception_type,
            exception_message,
        )

    return None


async def store_access_token(
    cache: Cache,
    access_token: str,
    expires_in: int,
) -> None:
    """Store access token to cache along with a lock key whose expiry is 90% of
    the actual access token expiry

    The goal is to leave room for the refresh script to renew the token before
    it actually expires and to spare an API call from the latency of generating
    a new token.
    """

    try:
        await cache.set(CACHE_KEY, access_token)

        expiry = expires_in * 90 // 100

        await cache.set(
            LOCK_KEY,
            f"{datetime.now() + timedelta(seconds=expiry)}",
            ex=expiry,
        )
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.error(
            "Failed to cache dailymotion access token: "
            "exception_type=%s, exception_message=%s",
            exception_type,
            exception_message,
        )
