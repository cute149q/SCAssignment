from dataclasses import dataclass
from app.repositories.timer_repo import RedisTimerRepository


@dataclass
class Dependencies:
    timer_repository: RedisTimerRepository
