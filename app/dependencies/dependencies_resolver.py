from dataclasses import dataclass
from typing import ClassVar

from app.dependencies.timer_repo_client import get_redis_db_client
from app.models.settings import AppSettings
from app.services.redis_timer_repository import RedisTimerRepository
from app.services.timer_executor import TimerExecutor


@dataclass
class Dependencies:
    timer_repository: RedisTimerRepository
    timer_executor: TimerExecutor


class DependenciesResolver:
    _dependencies: ClassVar[Dependencies | None] = None

    @classmethod
    async def init_dependencies(cls, settings: AppSettings) -> None:
        timer_repo = RedisTimerRepository(redis_client=get_redis_db_client(settings))
        cls._dependencies = Dependencies(
            timer_repository=timer_repo,
            timer_executor=TimerExecutor(timer_repository=timer_repo),
        )

    @classmethod
    def _get_deps(cls) -> Dependencies:
        if cls._dependencies is None:
            raise RuntimeError("Dependencies not initialized")
        return cls._dependencies

    @classmethod
    def get_timer_repository(cls) -> RedisTimerRepository:
        return cls._get_deps().timer_repository

    @classmethod
    def get_timer_executor(cls) -> TimerExecutor:
        return cls._get_deps().timer_executor

    @classmethod
    async def destroy(cls) -> None:
        if cls._dependencies is None:
            return

        if cls._dependencies.timer_executor is not None:
            await cls._dependencies.timer_executor.close()
        cls._dependencies = None
