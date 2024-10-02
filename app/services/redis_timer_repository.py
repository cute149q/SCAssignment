from app.repositories.timer_repo import TimerRepository

from redis.asyncio.cluster import RedisCluster


class RedisTimerRepository(TimerRepository):
    def __init__(self, redis_client: RedisCluster) -> None:
        self.redis_client = redis_client

    async def get_timer(self, timer_id: str) -> dict:
        timer = await self.redis_client.hgetall(timer_id)
        if not timer:
            return None
        return timer

    async def create_timer(self, timer: dict) -> dict:
        timer_id = timer["id"]
        await self.redis_client.hset(
            timer_id,
            mapping=timer,
        )
        return timer

    async def purge_timers(self):
        await self.redis_client.flushall()
