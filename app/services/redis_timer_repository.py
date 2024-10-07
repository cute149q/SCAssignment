import logging
import sys

from redis.asyncio import Redis

from app.repositories.timer_repo import TimerRepository

TIMER_PREFIX = "timer#"


class RedisTimerRepository(TimerRepository):
    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter(
            "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
        )
        stream_handler.setFormatter(log_formatter)
        self.logger.addHandler(stream_handler)

    async def get_timer(self, timer_id: str) -> dict:
        self.logger.info(f"Getting timer with id {timer_id}")
        timer = await self.redis_client.hgetall(f"{TIMER_PREFIX}{timer_id}")
        self.logger.info(f"Retrieved timer: {timer}")
        if not timer:
            return None
        return timer

    async def create_timer(self, timer: dict) -> dict:
        timer_id = timer["id"]
        self.logger.info(f"Received timer: {timer}")
        await self.redis_client.hset(
            f"{TIMER_PREFIX}{timer_id}",
            mapping=timer,
        )
        return timer

    async def purge_timers(self):
        await self.redis_client.flushall()
