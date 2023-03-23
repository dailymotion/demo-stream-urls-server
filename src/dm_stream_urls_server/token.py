import json
import logging

import aiohttp

from dm_stream_urls_server.cache import (
    Cache,
    is_access_token_expired,
    read_access_token,
    store_access_token,
)
from dm_stream_urls_server.config import (
    DAILYMOTION_API_CREDENTIALS_FILE,
    DAILYMOTION_API_OAUTH_TOKEN_URL,
)

logger = logging.getLogger(__name__)


def get_dailymotion_api_credentials(
    credentials_filename: str,
) -> tuple[str, str]:
    """
    File format is:
    {
        "DAILYMOTION_API_KEY_ID": <client_id>,
        "DAILYMOTION_API_KEY_SECRET": <client_secret>
    }"""

    with open(credentials_filename, "r", encoding="utf8") as fh:
        creds = json.load(fh)

    return (
        creds.get("DAILYMOTION_API_KEY_ID"),
        creds.get("DAILYMOTION_API_KEY_SECRET"),
    )


async def fetch_dailymotion_api_oauth_token() -> dict:
    """Generate an access token from Dailymotion API"""

    client_id, client_secret = get_dailymotion_api_credentials(
        DAILYMOTION_API_CREDENTIALS_FILE
    )

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.post(
            url=DAILYMOTION_API_OAUTH_TOKEN_URL,
            data={
                "scope": "read_video_streams",
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=2,
        ) as response:
            response_json: dict = await response.json()

            return response_json


async def get_dailymotion_api_access_token(cache: Cache) -> str | None:
    """Return cached access token

    If the cache is missing, fetch a new token and save it to cache and
    return it."""

    if access_token := await read_access_token(cache):
        return access_token

    await refresh_dailymotion_api_access_token(cache)

    return await read_access_token(cache)


async def refresh_dailymotion_api_access_token(cache: Cache) -> None:
    """Fetch a new access token if the cache has expired"""

    if not await is_access_token_expired(cache):
        return

    try:
        response = await fetch_dailymotion_api_oauth_token()
        access_token = response["access_token"]

        if access_token:
            logger.debug("Generated access token from dailymotion.com")

            await store_access_token(
                cache=cache,
                access_token=access_token,
                expires_in=response["expires_in"],
            )
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.error(
            "Failed to get dailymotion access token: "
            "exception_type=%s, exception_message=%s",
            exception_type,
            exception_message,
        )
