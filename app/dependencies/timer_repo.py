from app.services.redis_timer_repository import RedisTimerRepository
from dependencies_resolver import DependenciesResolver


def get_timer_repo_service() -> RedisTimerRepository:
    return DependenciesResolver.get_timer_repository()
