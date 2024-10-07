import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services.redis_timer_repository import RedisTimerRepository


@pytest.fixture
def redis_client():
    return AsyncMock()


@pytest.fixture
def redis_timer_repository(redis_client):
    return RedisTimerRepository(redis_client)


@pytest.mark.asyncio
async def test_get_timer(redis_timer_repository, redis_client):
    timer_id = "123"
    expected_timer = {"id": "123", "name": "test_timer"}
    redis_client.hgetall.return_value = expected_timer

    timer = await redis_timer_repository.get_timer(timer_id)

    redis_client.hgetall.assert_called_once_with(f"timer#{timer_id}")
    assert timer == expected_timer


@pytest.mark.asyncio
async def test_get_timer_not_found(redis_timer_repository, redis_client):
    timer_id = "123"
    redis_client.hgetall.return_value = {}

    timer = await redis_timer_repository.get_timer(timer_id)

    redis_client.hgetall.assert_called_once_with(f"timer#{timer_id}")
    assert timer is None


@pytest.mark.asyncio
async def test_create_timer(redis_timer_repository, redis_client):
    timer = {"id": "123", "name": "test_timer"}

    result = await redis_timer_repository.create_timer(timer)

    redis_client.hset.assert_called_once_with(f"timer#123", mapping=timer)
    assert result == timer


@pytest.mark.asyncio
async def test_purge_timers(redis_timer_repository, redis_client):
    await redis_timer_repository.purge_timers()

    redis_client.flushall.assert_called_once()
