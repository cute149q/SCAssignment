import json
import time
from datetime import datetime, timezone

import pytest
import requests
from fastapi.encoders import jsonable_encoder
from pytest_httpserver import HTTPServer
from redis.asyncio import Redis

from app.models.api import ErrorCode
from app.models.timer import SetTimerRequest


@pytest.fixture(autouse=True)
def clean_timer_redis_cache(redis_client: Redis):
    redis_client.flushall()
    yield
    redis_client.flushall()


def test_post_timer_request(base_url: str, httpserver: HTTPServer) -> None:
    httpserver.expect_request("/", method="post").respond_with_data("OK")
    set_timer_request = SetTimerRequest(
        hours=0,
        minutes=0,
        seconds=15,
        url=httpserver.url_for("/"),
    )
    response = requests.post(f"{base_url}/timer", json=jsonable_encoder(set_timer_request))
    time.sleep(2)
    assert response.status_code == 201
    content = json.loads(response.text)
    assert content["errors"] == []
    assert 10 <= content["data"][0]["time_left"] <= 15
    httpserver.check_assertions()


def test_get_timer_request_in_cache(base_url: str) -> None:
    # Set a timer
    set_timer_request = SetTimerRequest(
        hours=0,
        minutes=0,
        seconds=15,
        url="https://example.com",
    )
    response = requests.post(f"{base_url}/timer", json=jsonable_encoder(set_timer_request))
    time.sleep(1)
    assert response.status_code == 201
    content = json.loads(response.text)
    assert content["errors"] == []
    assert 10 <= content["data"][0]["time_left"] <= 15
    # Get the timer
    timer_id = content["data"][0]["id"]
    response = requests.get(f"{base_url}/timer/{timer_id}")
    assert response.status_code == 200
    content = json.loads(response.text)
    assert content["errors"] == []
    assert content["data"][0]["id"] == timer_id
    assert 0 <= content["data"][0]["time_left"] <= 15


def test_get_timer_request_not_in_cache(base_url: str) -> None:
    response = requests.get(f"{base_url}/timer/1")
    assert response.status_code == 404
    content = json.loads(response.text)
    assert content["errors"] != []
    assert content["errors"][0]["code"] == ErrorCode.NOT_FOUND
    assert content["errors"][0]["message"] == "Timer with id 1 not found"


def test_get_timer_request_expired(base_url: str) -> None:
    # Set a timer
    set_timer_request = SetTimerRequest(
        hours=0,
        minutes=0,
        seconds=1,
        url="https://example.com",
    )
    response = requests.post(f"{base_url}/timer", json=jsonable_encoder(set_timer_request))
    timer_id = response.json()["data"][0]["id"]
    time.sleep(2)
    response = requests.get(f"{base_url}/timer/{timer_id}")

    assert response.status_code == 200
    content = json.loads(response.text)
    assert content["errors"] == []
    assert content["data"][0]["id"] == timer_id
    assert content["data"][0]["time_left"] == 0
