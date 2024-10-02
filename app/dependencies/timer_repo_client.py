from redis.asyncio.cluster import RedisCluster

from models.settings import AppSettings

DEFAULT_REDIS_TIMEOUT_SECONDS = 5


def get_redis_db_client(settings: AppSettings) -> RedisCluster:
    return RedisCluster(
        host=settings.timer_db_endpoint,
        port=settings.timer_db_port,
        ssl=settings.timer_db_ssl_enabled,
        ssl_cert_reqs="none",
        socket_timeout=DEFAULT_REDIS_TIMEOUT_SECONDS,
        decode_responses=True,
    )
