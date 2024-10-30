import logging
import sys
from datetime import datetime, timezone

from redis.asyncio import Redis

from app.models.timer import TimerTask
from app.repositories.timer_repo import TimerRepository


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
        self.EXECUTED_PREFIX = "executed:"
        self.TIMER_PREFIX = "timer:"

    async def get_timer(self, timer_id: str) -> TimerTask | None:
        self.logger.info(f"Getting timer with id {timer_id}")
        timer_json = await self.redis_client.get(f"{self.TIMER_PREFIX}{timer_id}")  # type: ignore
        self.logger.info(f"Retrieved timer: {timer_json}")
        if not timer_json:
            return None
        return TimerTask.model_validate_json(timer_json)

    async def delete_timer(self, timer_id: str) -> TimerTask | None:
        await self.redis_client.zrem(f"{self.TIMER_PREFIX}task_set", timer_id)  # type: ignore
        timer_json = await self.redis_client.getdel(f"{self.TIMER_PREFIX}{timer_id}")  # type: ignore
        if timer_json is None:
            return None
        return TimerTask.model_validate_json(timer_json)

    async def create_timer(self, timer: TimerTask) -> None:
        await self.redis_client.set(  # type: ignore
            f"{self.TIMER_PREFIX}{timer.timer_id}",
            timer.model_dump_json(),
        )
        self.logger.info(f"Created timer: {timer.model_dump_json()}")
        timer_mapping = {
            timer.timer_id: timer.expires_at.timestamp(),
        }
        response = await self.redis_client.zadd(f"{self.TIMER_PREFIX}task_set", timer_mapping)  # type: ignore
        if response == 0:
            raise Exception("Failed to add timer to task set")
        self.logger.info(f"Added timer to task set: {timer_mapping}")

    async def get_scheduled_task_id(self) -> str | None:
        task_ids = await self.redis_client.zrange(f"{self.TIMER_PREFIX}task_set", start=-1, end=datetime.now(timezone.utc).timestamp(), byscore=True)  # type: ignore
        if not task_ids:
            return None
        return task_ids[0]

    async def add_executed_task(self, timer: TimerTask) -> None:
        await self.redis_client.set(  # type: ignore
            f"{self.EXECUTED_PREFIX}{timer.timer_id}",
            timer.model_dump_json(),
        )
        self.logger.info(f"Added executed task: {timer.model_dump_json()}")

    async def get_executed_task(self, timer_id: str) -> TimerTask | None:
        timer_json = await self.redis_client.get(f"{self.EXECUTED_PREFIX}{timer_id}")
        if not timer_json:
            return None
        return TimerTask.model_validate_json(timer_json)
