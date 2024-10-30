import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import ANY, AsyncMock, patch

import pytest

from app.models.timer import TimerTask
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
    expected_timer = TimerTask(
        timer_id=timer_id, url="http://test.com", expires_at="2024-10-09T00:17:20.501912Z"
    ).model_dump_json()
    redis_client.get.return_value = expected_timer

    timer = await redis_timer_repository.get_timer(timer_id)

    redis_client.get.assert_called_once_with(f"timer:{timer_id}")
    assert timer.model_dump_json() == expected_timer


@pytest.mark.asyncio
async def test_get_timer_not_found(redis_timer_repository, redis_client):
    timer_id = "123"
    redis_client.get.return_value = None

    timer = await redis_timer_repository.get_timer(timer_id)

    redis_client.get.assert_called_once_with(f"timer:{timer_id}")
    assert timer is None


@pytest.mark.asyncio
async def test_create_timer(redis_timer_repository, redis_client):
    timer = TimerTask(timer_id="123", url="http://test.com", expires_at="2024-10-09T00:17:20.501912Z")
    redis_client.zadd.return_value = 1
    redis_client.set.return_value = None
    result = await redis_timer_repository.create_timer(timer)

    redis_client.set.assert_called_once_with(
        "timer:123",
        timer.model_dump_json(),
    )
    timer_mapping = {
        timer.timer_id: timer.expires_at.timestamp(),
    }
    redis_client.zadd.assert_called_once_with(
        "timer:task_set",
        timer_mapping,
    )
    assert result is None


@pytest.mark.asyncio
async def test_create_timer_failed(redis_timer_repository, redis_client):
    timer = TimerTask(timer_id="123", url="http://test.com", expires_at="2024-10-09T00:17:20.501912Z")
    redis_client.zadd.return_value = 0
    redis_client.set.return_value = None
    with pytest.raises(Exception):
        await redis_timer_repository.create_timer(timer)


@pytest.mark.asyncio
async def test_delete_timer(redis_timer_repository, redis_client):
    timer_id = "123"
    timer = TimerTask(timer_id=timer_id, url="http://test.com", expires_at="2024-10-09T00:17:20.501912Z")
    redis_client.getdel.return_value = timer.model_dump_json()
    redis_client.zrem.return_value = None

    result = await redis_timer_repository.delete_timer(timer_id)

    redis_client.zrem.assert_called_once_with("timer:task_set", timer_id)
    redis_client.getdel.assert_called_once_with(f"timer:{timer_id}")
    assert result.model_dump_json() == timer.model_dump_json()


@pytest.mark.asyncio
async def test_delete_timer_not_found(redis_timer_repository, redis_client):
    timer_id = "123"
    redis_client.getdel.return_value = None

    result = await redis_timer_repository.delete_timer(timer_id)

    redis_client.getdel.assert_called_once_with(f"timer:{timer_id}")
    assert result is None


@pytest.mark.asyncio
async def test_get_scheduled_task_id(redis_timer_repository, redis_client):
    timer_id = "123"
    redis_client.zrange.return_value = [timer_id]

    task_id = await redis_timer_repository.get_scheduled_task_id()

    redis_client.zrange.assert_called_once_with(
        "timer:task_set",
        start=-1,
        end=ANY,
        byscore=True,
    )
    assert task_id == timer_id


@pytest.mark.asyncio
async def test_get_scheduled_task_id_not_found(redis_timer_repository, redis_client):
    redis_client.zrange.return_value = []

    task_id = await redis_timer_repository.get_scheduled_task_id()

    redis_client.zrange.assert_called_once_with(
        "timer:task_set",
        start=-1,
        end=ANY,
        byscore=True,
    )
    assert task_id is None
