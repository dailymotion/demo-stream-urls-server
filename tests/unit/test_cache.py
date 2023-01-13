from unittest.mock import AsyncMock, call, patch

import pytest

from freezegun import freeze_time
from redis import exceptions
from redis.asyncio import Redis

from dm_stream_urls_server.cache import (
    get_cache,
    is_access_token_expired,
    read_access_token,
    store_access_token,
)


@patch("dm_stream_urls_server.cache.Redis.from_url")
@pytest.mark.parametrize(
    "from_url_side_effect, expected_return",
    (
        (
            (exceptions.RedisError(),),
            None,
        ),
        (
            (Redis(),),
            Redis(),
        ),
    ),
)
def test_get_cache(
    redis_from_url,
    from_url_side_effect,
    expected_return,
):
    redis_from_url.side_effect = from_url_side_effect

    assert isinstance(get_cache(), type(expected_return))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_side_effect, expected_return",
    (
        (
            (None,),
            True,
        ),
        (
            (b"2010-09-08T07:06:05",),
            False,
        ),
        (
            (exceptions.RedisError,),
            True,
        ),
    ),
)
async def test_is_access_token_expired(
    get_side_effect,
    expected_return,
):
    redis = AsyncMock(autospec=Redis)
    redis.get.side_effect = get_side_effect

    assert expected_return == await is_access_token_expired(redis)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_side_effect, expected_return",
    (
        (
            (None,),
            None,
        ),
        (
            (b"test-access-token",),
            "test-access-token",
        ),
        (
            (exceptions.RedisError,),
            None,
        ),
    ),
)
async def test_read_access_token(
    get_side_effect,
    expected_return,
):
    redis = AsyncMock(autospec=Redis)
    redis.get.side_effect = get_side_effect

    assert expected_return == await read_access_token(redis)


@pytest.mark.asyncio
@freeze_time("2012-11-10T09:08:07Z")
async def test_store_access_token():
    redis = AsyncMock(autospec=Redis)

    await store_access_token(redis, "test-access-token", 100)

    assert 2 == redis.set.call_count
    redis.set.assert_has_awaits(
        [
            call(
                "dailymotion_api_access_token",
                "test-access-token",
            ),
            call(
                "dailymotion_api_access_token_cached",
                "2012-11-10 09:09:37",
                ex=90,
            ),
        ]
    )
