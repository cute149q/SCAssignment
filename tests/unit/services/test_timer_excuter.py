import asyncio
import time
from datetime import datetime, timedelta, timezone
from types import coroutine
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from app.models.timer import TimerTask
from app.repositories.timer_repo import TimerRepository
from app.services.redis_timer_repository import RedisTimerRepository
from app.services.timer_executor import Response, TimerExecutor, get_response_message


@pytest.fixture
async def timer_repo_mock():
    mock = AsyncMock(spec=TimerRepository)
    return mock


@pytest.fixture
async def timer_executor(timer_repo_mock) -> TimerExecutor:
    return TimerExecutor(
        timer_repository=timer_repo_mock,
    )


def test_get_response_message():
    assert get_response_message(200) == "OK"
    assert get_response_message(400) == "Bad Request"
    assert get_response_message(404) == "Not Found"
    assert get_response_message(408) == "Request Timeout"
    assert get_response_message(500) == "Internal Server Error"
    assert get_response_message(503) == "Service Unavailable"
    assert get_response_message(504) == "Gateway Timeout"
    assert get_response_message(999) == "Unknown Error"


@pytest.mark.asyncio
async def test_timer_executor_start(timer_executor):
    await timer_executor.start()
    assert timer_executor.http_session is not None
    assert timer_executor.task is not None


@pytest.mark.asyncio
async def test_timer_executor_start_exception(timer_executor):
    with patch("aiohttp.ClientSession") as mock:
        mock.side_effect = Exception("Failed to start")
        with pytest.raises(Exception):
            await timer_executor.start()


@pytest.mark.asyncio
async def test_timer_executor_stop(timer_executor):
    timer_executor.timer_repository.get_scheduled_task_id.return_value = None
    await timer_executor.start()
    await timer_executor.close()
    assert timer_executor.task._state == "CANCELLED"


@pytest.mark.asyncio
async def test_timer_executor_execute_task(timer_executor):
    timer = TimerTask(
        timer_id="123",
        url="http://test.com",
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat(),
    )

    timer_executor.timer_repository.get_scheduled_task_id.return_value = timer.timer_id
    timer_executor.timer_repository.get_timer.return_value = timer

    await timer_executor.start()
    with patch("aiohttp.ClientSession.post") as mock:
        mock.return_value.__aenter__.return_value.status = 200
        await timer_executor.execute_task(url=str(timer.url), timer_id=timer.timer_id)
        assert mock.called


@pytest.mark.asyncio
async def test_timer_executor_execute_task_exception(timer_executor):
    timer = TimerTask(
        timer_id="123",
        url="http://test.com",
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat(),
    )

    timer_executor.timer_repository.get_scheduled_task_id.return_value = timer.timer_id
    timer_executor.timer_repository.get_timer.return_value = timer
    timer_executor.logger.error = AsyncMock()

    await timer_executor.start()
    with patch("aiohttp.ClientSession.post") as mock:
        mock.side_effect = aiohttp.ClientError("Failed to get")
        await timer_executor.execute_task(url=str(timer.url), timer_id=timer.timer_id)
        assert mock.called
        assert timer_executor.logger.error.called


@pytest.mark.asyncio
async def test_timer_scheduler_start(timer_executor):
    timer = TimerTask(
        timer_id="123",
        url="http://test.com",
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat(),
    )

    timer_executor.timer_repository.get_scheduled_task_id.return_value = timer.timer_id
    timer_executor.timer_repository.delete_timer.return_value = timer

    await timer_executor.start()
    await asyncio.sleep(0.1)
    assert timer_executor.task is not None
    assert timer_executor.task._state == "PENDING"
    await asyncio.sleep(2)
    timer_executor.task.cancel()
    assert timer_executor.timer_repository.delete_timer.called
    assert timer_executor.timer_repository.get_scheduled_task_id.called
