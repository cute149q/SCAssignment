from app.dependencies.dependencies_resolver import DependenciesResolver
from app.services.redis_timer_repository import RedisTimerRepository
from app.services.timer_executor import TimerExecutor


def get_timer_repo_service() -> RedisTimerRepository:
    return DependenciesResolver.get_timer_repository()


def get_timer_executor_service() -> TimerExecutor:
    return DependenciesResolver.get_timer_executor()
