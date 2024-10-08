from datetime import datetime, timedelta, timezone
from types import coroutine
from unittest.mock import patch

import pytest

from app.models.timer import TimerTask
from app.services.timer_executor import Response, TimerExecutor, get_response_message


@pytest.fixture
async def timer_executor() -> TimerExecutor:
    return TimerExecutor()


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
async def test_timer_executor_create_task(timer_executor: TimerExecutor):
    timer_task = TimerTask(
        timer_id="timer_id",
        url="http://example.com",
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=10)).timestamp(),
    )

    with patch.object(timer_executor.http_session, "get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        response = await timer_executor.create_task(timer_task)
    assert response.status == 200
    assert mock_get.called


@pytest.mark.asyncio
async def test_timer_executor_add_task(timer_executor: TimerExecutor):
    timer_task = TimerTask(
        timer_id="timer_id",
        url="http://example.com",
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=10)).timestamp(),
    )
    with patch.object(timer_executor, "create_task") as mock_create_task:
        mock_create_task.return_value = Response(200)
        timer_executor.add_task(timer_task)
    assert timer_task.id in timer_executor.tasks


@pytest.mark.asyncio
async def test_timer_executor_purge_tasks(timer_executor: TimerExecutor):
    timer_task_1 = TimerTask(
        timer_id="timer_id_1",
        url="http://example.com",
        expires_at=(datetime.now(timezone.utc) + timedelta(seconds=100)).timestamp(),
    )
    timer_task_2 = TimerTask(
        timer_id="timer_id_2",
        url="http://example.com",
        expires_at=(datetime.now(timezone.utc) - timedelta(seconds=100)).timestamp(),
    )

    timer_executor.add_task(timer_task_1)
    timer_executor.add_task(timer_task_2)
    await timer_executor.purge_all_tasks()

    assert not timer_executor.tasks
