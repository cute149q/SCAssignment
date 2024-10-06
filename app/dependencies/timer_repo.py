from app.dependencies.dependencies_resolver import DependenciesResolver
from app.services.redis_timer_repository import RedisTimerRepository


def get_timer_repo_service() -> RedisTimerRepository:
    return DependenciesResolver.get_timer_repository()
