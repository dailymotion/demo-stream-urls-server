from contextlib import nullcontext as does_not_raise
from unittest.mock import Mock, patch

import aiohttp
import pytest

from fastapi import HTTPException, Request

from dm_stream_urls_server.api import (
    get_access_token,
    get_client_ip,
    get_stream_urls_route,
)


@pytest.mark.parametrize(
    "fastapi_request, client_ip, expected_return",
    (
        (
            Request(scope={"type": "http"}),
            None,
            None,
        ),
        (
            Request(scope={"type": "http", "client": None}),
            None,
            None,
        ),
        (
            Request(
                scope={"type": "http", "client": ("101.102.103.104", None)}
            ),
            None,
            "101.102.103.104",
        ),
        (
            Request(
                scope={"type": "http", "client": ("101.102.103.104", 6128)}
            ),
            None,
            "101.102.103.104",
        ),
        (
            Request(
                scope={"type": "http", "client": ("101.102.103.104", 6128)}
            ),
            "201.202.203.204",
            "201.202.203.204",
        ),
    ),
)
def test_get_client_ip(fastapi_request, client_ip, expected_return):
    assert expected_return == get_client_ip(
        request=fastapi_request,
        client_ip=client_ip,
    )


@pytest.mark.asyncio
@patch("dm_stream_urls_server.api.get_dailymotion_api_access_token")
async def test_get_access_token(
    get_cached_dailymotion_api_access_token,
):
    cache = Mock()

    await get_access_token(cache)

    get_cached_dailymotion_api_access_token.assert_awaited_once_with(cache)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_stream_urls_side_effect, expected_exception",
    (
        (
            None,
            does_not_raise(),
        ),
        (
            (
                aiohttp.ClientResponseError(
                    request_info=None,
                    history=(),
                    status=404,
                    message="Not found",
                ),
            ),
            pytest.raises(HTTPException),
        ),
        (
            (RuntimeError(),),
            pytest.raises(HTTPException),
        ),
    ),
)
@patch("dm_stream_urls_server.api.get_stream_urls")
async def test_get_stream_urls_route(
    get_stream_urls,
    get_stream_urls_side_effect,
    expected_exception,
):
    video_id = "xVideoId"
    video_formats = "format1,format2"
    client_ip = "a.b.c.d"
    authorization = "test-token"

    get_stream_urls.side_effect = get_stream_urls_side_effect

    with expected_exception:
        await get_stream_urls_route(
            video_id,
            video_formats,
            client_ip,
            authorization,
        )

    get_stream_urls.assert_awaited_once_with(
        video_id=video_id,
        video_formats=video_formats,
        client_ip=client_ip,
        authorization=authorization,
    )
