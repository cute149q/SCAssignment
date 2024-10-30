import os

import pytest
from redis.asyncio import Redis


@pytest.fixture
def base_url() -> str:
    return os.environ.get("TIMER_API_URL")


@pytest.fixture
def redis_url() -> str:
    return os.environ.get("TIMER_REDIS_URL")


@pytest.fixture
def redis_client() -> Redis:
    return Redis(
        host=os.environ.get("TIMER_REDIS_HOST"),
        port=os.environ.get("TIMER_REDIS_PORT"),
        ssl=os.environ.get("TIMER_REDIS_SSL_ENABLED"),
        ssl_cert_reqs="none",
        socket_timeout=5,
        decode_responses=True,
    )
