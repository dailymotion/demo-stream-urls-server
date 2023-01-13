from unittest.mock import AsyncMock, patch

import pytest

from redis.asyncio import Redis

from dm_stream_urls_server.token import (
    fetch_dailymotion_api_oauth_token,
    get_dailymotion_api_access_token,
    get_dailymotion_api_credentials,
    refresh_dailymotion_api_access_token,
)


def test_get_dailymotion_api_credentials():
    assert (
        "tests-fixtures-creds-client-id",
        "tests-fixtures-creds-client-secret",
    ) == get_dailymotion_api_credentials("tests/fixtures/creds.json")


@pytest.mark.asyncio
@patch("aiohttp.client.ClientSession._request")
@patch("dm_stream_urls_server.token.get_dailymotion_api_credentials")
async def test_get_dailymotion_api_access_token(
    get_credentials,
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

    get_credentials.return_value = ("test-client-id", "test-client-secret")

    aiohttp_request.return_value = MockResponse()

    assert await fetch_dailymotion_api_oauth_token() == {
        "this": "is",
        "a": "test",
    }

    aiohttp_request.assert_awaited_with(
        "POST",
        "https://partner.api.dailymotion.com/oauth/v1/token",
        data={
            "scope": "upload_videos read_videos edit_videos delete_videos",
            "grant_type": "client_credentials",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=2,
    )


@pytest.mark.asyncio
@patch("dm_stream_urls_server.token.refresh_dailymotion_api_access_token")
@patch("dm_stream_urls_server.token.read_access_token")
@pytest.mark.parametrize(
    "redis, cached_access_token, expected_return",
    (
        (
            AsyncMock(autospec=Redis),
            ("cached-access-token",),
            "cached-access-token",
        ),
        (
            AsyncMock(autospec=Redis),
            (None, "new-access-token"),
            "new-access-token",
        ),
    ),
)
async def test_get_dailymotion_api_access_token(
    m_read_access_token,
    m_refresh_dailymotion_api_access_token,
    redis,
    cached_access_token,
    expected_return,
):
    m_read_access_token.side_effect = cached_access_token

    assert expected_return == await get_dailymotion_api_access_token(redis)

    if len(cached_access_token) > 1:
        m_refresh_dailymotion_api_access_token.assert_awaited()
    else:
        m_refresh_dailymotion_api_access_token.assert_not_awaited()


@pytest.mark.asyncio
@patch("dm_stream_urls_server.token.store_access_token")
@patch("dm_stream_urls_server.token.fetch_dailymotion_api_oauth_token")
@patch("dm_stream_urls_server.token.is_access_token_expired")
@pytest.mark.parametrize(
    "is_access_token_expired, fetched_access_token",
    (
        (
            False,
            None,
        ),
        (
            True,
            {"access_token": "fetched-access-token", "expires_in": 100},
        ),
    ),
)
async def test_refresh_dailymotion_api_access_token(
    m_is_access_token_expired,
    m_fetch_dailymotion_api_oauth_token,
    m_store_access_token,
    is_access_token_expired,
    fetched_access_token,
):
    redis = AsyncMock(Redis)

    m_is_access_token_expired.return_value = is_access_token_expired
    m_fetch_dailymotion_api_oauth_token.return_value = fetched_access_token

    await refresh_dailymotion_api_access_token(redis)

    if is_access_token_expired:
        m_fetch_dailymotion_api_oauth_token.assert_awaited()
    else:
        m_fetch_dailymotion_api_oauth_token.assert_not_awaited()

    if fetched_access_token:
        m_store_access_token.assert_awaited_once_with(
            cache=redis,
            **fetched_access_token,
        )
    else:
        m_store_access_token.assert_not_awaited()
