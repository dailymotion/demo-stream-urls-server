import ipaddress
import logging

from pathlib import Path

import aiohttp

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from dm_stream_urls_server.cache import Cache, get_cache
from dm_stream_urls_server.stream import get_stream_urls
from dm_stream_urls_server.token import get_dailymotion_api_access_token

logger = logging.getLogger(__name__)

app = FastAPI()


async def get_client_public_ip() -> str | None:
    """Call ifconfig.me API to detect public IP address"""

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://ifconfig.me/all.json",
        ) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError:
                return None

            response_json: dict[str, str] = await response.json()

            return response_json.get("ip_addr")


async def get_client_ip(
    request: Request,
    client_ip: str | None = None,
) -> str | None:
    """Helper to get client IP address"""

    if client_ip:
        return client_ip

    if request.client:
        request_client_ip = request.client.host

        if ipaddress.ip_address(request_client_ip).is_private:
            return await get_client_public_ip()

        return request_client_ip

    return None


async def get_access_token(cache: Cache = Depends(get_cache)) -> str | None:
    """Helper for FastAPI to get cached access token"""

    return await get_dailymotion_api_access_token(cache)


@app.get("/")
async def redirect_homepage_to_docs():
    """Redirect Homepage to /docs"""

    return RedirectResponse(url="/demo")


@app.get("/stream-urls")
async def get_stream_urls_route(
    video_id: str,
    video_formats: str,
    client_ip: str = Depends(get_client_ip),
    authorization: str = Depends(get_access_token),
):
    """Request Dailymotion API to get video stream URLs"""

    try:
        return await get_stream_urls(
            video_id=video_id,
            video_formats=video_formats,
            client_ip=client_ip,
            authorization=authorization,
        )
    except aiohttp.ClientResponseError as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.message,
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.error(
            "Failed to get stream URL: "
            "client_ip=%s, video_id=%s, video_formats=%s, "
            "exception_type=%s, exception_message=%s",
            client_ip,
            video_id,
            video_formats,
            exception_type,
            exception_message,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@app.get("/permanent-stream-url")
async def get_permanent_stream_url_route(
    video_id: str,
    video_format: str,
    client_ip: str = Depends(get_client_ip),
    authorization: str = Depends(get_access_token),
):
    """Request Dailymotion API to get a video stream URL and redirect to it"""

    try:
        stream_urls = await get_stream_urls(
            video_id=video_id,
            video_formats=video_format,
            client_ip=client_ip,
            authorization=authorization,
        )

    except aiohttp.ClientResponseError as e:
        raise HTTPException(
            status_code=e.status,
            detail=e.message,
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        exception_type = type(e).__name__
        exception_message = str(e)

        logger.error(
            "Failed to get stream URL: "
            "client_ip=%s, video_id=%s, video_format=%s, "
            "exception_type=%s, exception_message=%s",
            client_ip,
            video_id,
            video_format,
            exception_type,
            exception_message,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

    try:
        stream_url = stream_urls[video_format]
    except (KeyError, TypeError):
        stream_url = None

    if not stream_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format {video_format} not found",
        )

    return RedirectResponse(stream_url)


app.mount(
    "/demo",
    StaticFiles(directory=Path(__file__).parent.joinpath("demo"), html=True),
    name="demo",
)
