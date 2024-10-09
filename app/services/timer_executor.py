import asyncio
import logging
import sys
from contextlib import AsyncExitStack
from typing import Optional

import aiohttp

from app.repositories.timer_repo import TimerRepository


class Response:
    def __init__(self, status: int, content: Optional[str] = None):
        self.status = status
        self.content = content


def get_response_message(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 400:
            return "Bad Request"
        case 404:
            return "Not Found"
        case 408:
            return "Request Timeout"
        case 500:
            return "Internal Server Error"
        case 503:
            return "Service Unavailable"
        case 504:
            return "Gateway Timeout"
        case _:
            return "Unknown Error"


MAX_TIMEOUT_SECONDS = 5


class TimerExecutor:
    def __init__(self, timer_repository: TimerRepository) -> None:
        self.timer_repository = timer_repository
        self.exit_stack = AsyncExitStack()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter(
            "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
        )
        stream_handler.setFormatter(log_formatter)
        self.logger.addHandler(stream_handler)
        self.task = None

    async def start(self) -> None:
        self.http_session = await self.exit_stack.enter_async_context(aiohttp.ClientSession())

        async def _scheduler():
            try:
                self.logger.info("Scheduler started")
                while True:
                    await asyncio.sleep(0.1)
                    task_id = await self.timer_repository.get_scheduled_task_id()
                    if task_id is None:
                        continue
                    task = await self.timer_repository.delete_timer(task_id)
                    self.logger.info(f"Got task: {task}, and deleting it")
                    if task is None:
                        continue
                    await self.execute_task(str(task.url))
            except asyncio.CancelledError:
                self.logger.info("Stopping scheduler")

        self.task = asyncio.create_task(_scheduler())

    async def execute_task(self, url: str) -> None:
        self.logger.info(f"Executing task for url {url}")
        try:
            self.logger.info(f"Sending request to {url}")
            timeout = aiohttp.ClientTimeout(total=MAX_TIMEOUT_SECONDS)
            async with self.http_session.get(url, timeout=timeout) as response:
                self.logger.info(f"Executed task for url {url}")
                self.logger.info(f"Response status: {response.status}")
                self.logger.info(f"Response content: {await response.text()}")
        except aiohttp.ClientError as e:
            self.logger.error(f"Error executing task for url {url}: {e}")

    async def close(self):
        if self.task is not None:
            self.task.cancel()
        await self.exit_stack.aclose()
