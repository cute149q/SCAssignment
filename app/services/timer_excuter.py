import asyncio
import logging
import sys
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from app.models.timer import TimerTask


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


class TimerExecutor:
    def __init__(self):
        self.http_session = aiohttp.ClientSession()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter(
            "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
        )
        stream_handler.setFormatter(log_formatter)
        self.logger.addHandler(stream_handler)

        self.tasks = {}

    async def create_task(self, timer_task: TimerTask) -> Response:
        url = timer_task.url
        time_left = timer_task.expires_at - datetime.now(timezone.utc).timestamp()

        self.logger.info(f"Timer ID {timer_task.id} will fire in {time_left} seconds")

        if time_left > 0:
            await asyncio.sleep(time_left)

        response = await self.execute_task(url)

        if response.status == 200:
            self.logger.info(f"Succesfully fired webhook for Timer ID {timer_task.id}, response: {response.content}")
        elif response:
            self.logger.error(
                f"Failed to fire webhook for Timer ID {timer_task.id}, status code: {response.status}, response: {response.content}"
            )
        else:
            self.logger.error(f"Failed to fire webhook for Timer ID {timer_task.id}, unknown error. ")
        # Cleanup: Remove the task from the tasks dictionary
        self.tasks.pop(timer_task.id, None)
        return response

    async def execute_task(self, url: str) -> Response:
        try:
            async with self.http_session.get(url) as response:
                return Response(
                    status=response.status,
                    content=await response.text(),
                )
        except aiohttp.ClientError as e:
            return Response(
                status=500,
                content=str(e),
            )

    def add_task(self, timer_task: TimerTask):
        task = asyncio.create_task(self.create_task(timer_task))
        self.tasks[timer_task.timer_id] = task

    async def close(self):
        await self.http_session.close()
