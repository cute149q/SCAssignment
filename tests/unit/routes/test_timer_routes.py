import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from freezegun import freeze_time
from pytest_mock import MockerFixture, MockFixture

from app.dependencies.timer_repo import get_timer_executor_service, get_timer_repo_service
from app.main import app
from app.models.timer import SetTimerRequest
from app.services.redis_timer_repository import RedisTimerRepository
from app.services.timer_excuter import TimerExecutor

test_client = TestClient(app)


@pytest.fixture
def timer_executor_service_mock(mocker: MockFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=TimerExecutor)
    mock.add_task.return_value = None
    return mock


@pytest.fixture
def timer_repo_service_mock(mocker: MockFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=RedisTimerRepository)
    mock.create_timer.return_value = {"id": "1", "name": "test", "expires_at": "2021-08-01T00:00:00Z"}
    return mock


@pytest.fixture
def timer_url() -> str:
    return "/timer"


@pytest.fixture
def overrides(
    mocker: MockFixture,
    timer_executor_service_mock: AsyncMock,
    timer_repo_service_mock: AsyncMock,
):
    app.dependency_overrides = {
        get_timer_repo_service: lambda: timer_repo_service_mock,
        get_timer_executor_service: lambda: timer_executor_service_mock,
    }
    yield app.dependency_overrides
    app.dependency_overrides.clear()


def test_set_timer(overrides: dict, timer_url: str):
    timer_repo_service_mock = overrides[get_timer_repo_service]()
    timer_executor_service_mock = overrides[get_timer_executor_service]()

    response = test_client.post(
        timer_url,
        json={
            "hours": 1,
            "minutes": 0,
            "seconds": 0,
            "url": "http://example.com",
        },
    )
    assert response.status_code == 201
    response_content = json.loads(response.content)["data"][0]

    expires_at = datetime.fromisoformat(response_content["expires_at"]).timestamp()

    assert 3570 <= expires_at - datetime.now(timezone.utc).timestamp() <= 3600

    timer_repo_service_mock.create_timer.assert_called_once()
    timer_executor_service_mock.add_task.assert_called_once()


def test_set_timer_invalid_request(overrides: dict, timer_url: str):
    response = test_client.post(
        timer_url,
        json={
            "hours": 0,
            "minutes": 0,
            "seconds": 0,
            "url": "http://example.com",
        },
    )
    assert response.status_code == 400
    response_content = json.loads(response.content)["errors"][0]

    assert response_content["code"] == "invalid_request"
    assert response_content["message"] == "Timer duration must be greater than 0"


def test_get_timer_succeed(overrides: dict, timer_url: str):
    timer_repo_service_mock = overrides[get_timer_repo_service]()
    time_stamp = datetime.now(timezone.utc).timestamp()
    timer_repo_service_mock.get_timer.return_value = {
        "hours": "0",
        "minutes": "0",
        "seconds": "50",
        "url": "http://ipinfo.io/json",
        "id": "11c4dc54-759b-4172-b415-29de0373ffae",
        "expires_at": str(time_stamp + 50),
    }

    response = test_client.get(f"{timer_url}/11c4dc54-759b-4172-b415-29de0373ffae")

    assert response.status_code == 200
    response_content = json.loads(response.content)["data"][0]

    assert response_content["id"] == "11c4dc54-759b-4172-b415-29de0373ffae"
    assert 45 <= response_content["seconds_left"] <= 50


def test_get_timer_not_found(overrides: dict, timer_url: str):
    timer_repo_service_mock = overrides[get_timer_repo_service]()
    timer_repo_service_mock.get_timer.return_value = None

    response = test_client.get(f"{timer_url}/11c4dc54-759b-4172-b415-29de0373ffae")

    assert response.status_code == 404
    response_content = json.loads(response.content)["errors"][0]

    assert response_content["code"] == "not_found"
    assert response_content["message"] == "Timer with id 11c4dc54-759b-4172-b415-29de0373ffae not found"
