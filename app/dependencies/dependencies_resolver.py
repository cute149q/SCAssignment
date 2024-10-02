from dataclasses import dataclass
from app.dependencies.timer_repo_client import get_redis_db_client
from app.services.redis_timer_repository import RedisTimerRepository
from app.models.settings import AppSettings
from typing import ClassVar, Self


@dataclass
class Dependencies:
    timer_repository: RedisTimerRepository


class DependenciesResolver:

    _dependencies: ClassVar[Dependencies | None] = None

    @classmethod
    async def init_dependencies(cls, settings: AppSettings) -> Self:
        return cls(
            timer_repository=RedisTimerRepository(redis_client=get_redis_db_client(settings)),
        )

    @classmethod
    def _get_deps(cls) -> Dependencies:
        if cls._dependencies is None:
            raise RuntimeError("Dependencies not initialized")
        return cls._dependencies

    @classmethod
    def get_timer_repository(cls) -> RedisTimerRepository:
        return cls._get_deps().timer_repository
    

