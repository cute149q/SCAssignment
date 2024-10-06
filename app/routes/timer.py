import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Response

from app.dependencies.timer_repo import get_timer_repo_service
from app.models.api import ApiResponse
from app.models.timer import GetTimerResponse, SetTimerRequest
from app.repositories.timer_repo import TimerRepository

timer_router = APIRouter()


@timer_router.post("", response_model=ApiResponse[Any, Any])
async def set_timer(
    request: SetTimerRequest,
    response: Response,
    timer_repo: TimerRepository = Depends(get_timer_repo_service),
) -> ApiResponse[Any, Any]:
    timer_id = str(uuid.uuid4())
    total_seconds = request.hours * 3600 + request.minutes * 60 + request.seconds
    if total_seconds <= 0:
        response.status_code = 400
        return ApiResponse(
            error="Timer duration must be greater than 0",
        )
    expires_at = datetime.now(timezone.utc).timestamp() + total_seconds
    timer_dict = request.model_dump()
    timer_dict["id"] = timer_id
    timer_dict["expires_at"] = expires_at
    await timer_repo.create_timer(timer_dict)
    response.status_code = 201
    return ApiResponse(
        data={
            "id": timer_id,
            "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc),
        },
    )


@timer_router.get("/{timer_id}", response_model=ApiResponse[GetTimerResponse, Any])
async def get_timer(
    timer_id: str,
    response: Response,
    timer_repo: TimerRepository = Depends(get_timer_repo_service),
) -> ApiResponse[GetTimerResponse, Any]:
    timer = await timer_repo.get_timer(timer_id)
    if not timer:
        response.status_code = 404
        return ApiResponse(
            error="Timer not found",
        )

    expires_at = timer["expires_at"]
    seconds_left = expires_at - datetime.now(timezone.utc).timestamp()
    return ApiResponse(
        data=GetTimerResponse(id=timer_id, seconds_left=seconds_left),
    )
