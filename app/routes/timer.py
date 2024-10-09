import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from app.dependencies.timer_repo import get_timer_executor_service, get_timer_repo_service
from app.models.api import ApiResponse, ErrorCode, ErrorResponse
from app.models.timer import GetTimerResponse, SetTimerRequest, TimerTask
from app.repositories.timer_repo import TimerRepository
from app.services.timer_executor import TimerExecutor

timer_router = APIRouter()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


@timer_router.post("", response_model=ApiResponse[dict, dict])
async def set_timer(
    request: SetTimerRequest,
    response: Response,
    timer_repo: TimerRepository = Depends(get_timer_repo_service),
    timer_executor: TimerExecutor = Depends(get_timer_executor_service),
) -> ApiResponse[dict, dict]:
    timer_id = str(uuid.uuid4())
    total_seconds = request.hours * 3600 + request.minutes * 60 + request.seconds
    if total_seconds <= 0:
        response.status_code = 400
        return ApiResponse(
            errors=[
                ErrorResponse(
                    code=ErrorCode.INVALID_REQUEST,
                    message="Timer duration must be greater than 0",
                ).model_dump()
            ],
        )

    expires_at = datetime.now(timezone.utc).timestamp() + total_seconds

    timer = TimerTask(timer_id=timer_id, url=request.url, expires_at=expires_at)
    await timer_repo.create_timer(timer)

    response.status_code = 201
    return ApiResponse(
        data=[{"id": timer_id, "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat()}],
    )


@timer_router.get("/{timer_id}", response_model=ApiResponse[GetTimerResponse, Any])
async def get_timer(
    timer_id: str,
    response: Response,
    timer_repo: TimerRepository = Depends(get_timer_repo_service),
) -> ApiResponse[Any, Any]:
    timer = await timer_repo.get_timer(timer_id)
    if not timer:
        response.status_code = 404
        return ApiResponse(
            errors=[
                ErrorResponse(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Timer with id {timer_id} not found",
                )
            ]
        )

    seconds_remaining = (timer.expires_at - datetime.now(timezone.utc)).total_seconds()
    if seconds_remaining <= 0:
        seconds_remaining = 0
    return ApiResponse(
        data=[GetTimerResponse(id=timer_id, seconds_remaining=int(seconds_remaining))],
    )
