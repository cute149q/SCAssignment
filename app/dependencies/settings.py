from functools import lru_cache

from app.models.settings import AppSettings


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()  # type: ignore
