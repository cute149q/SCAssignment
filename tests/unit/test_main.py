import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.settings import AppSettings

client = TestClient(app)


@pytest.fixture
def dependency_overrides():
    yield app.dependency_overrides
    app.dependency_overrides = {}


@pytest.fixture
def overriden_app_settings(dependency_overrides) -> AppSettings:
    app_settings = AppSettings(
        stage="test",
        timer_db_endpoint="cache",
        timer_db_port=6379,
        timer_db_ssl_enabled=False,
    )
    dependency_overrides["get_app_settings"] = lambda: app_settings
    return app_settings


@pytest.mark.usefixtures("overriden_app_settings")
def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
