from unittest.mock import patch

import pytest

from dm_stream_urls_server.stream import get_stream_urls


@pytest.mark.asyncio
@patch("aiohttp.client.ClientSession._request")
async def test_get_stream_urls(
    aiohttp_request,
):
    class MockResponse:
        def release(self):
            ...

        async def json(self):
            return {
                "this": "is",
                "a": "test",
            }

    aiohttp_request.return_value = MockResponse()

    assert await get_stream_urls(
        video_id="xVideoId",
        video_formats="stream_format1_url,stream_format2_url",
        client_ip="101.102.103.104",
        authorization="test-authorization-header",
    ) == {
        "this": "is",
        "a": "test",
    }

    aiohttp_request.assert_awaited_with(
        "GET",
        "https://partner.api.dailymotion.com/rest/video/xVideoId",
        allow_redirects=True,
        params={
            "client_ip": "101.102.103.104",
            "fields": "stream_format1_url,stream_format2_url",
        },
        headers={
            "Authorization": "Bearer test-authorization-header",
        },
        timeout=2,
    )
