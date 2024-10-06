from enum import Enum
from typing import Any, Generic, Sequence, TypeVar

from fastapi import status
from pydantic import BaseModel, Field

DataItem = TypeVar("DataItem", dict, BaseModel)
ErrorItem = TypeVar("ErrorItem", dict, BaseModel)


class ErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    THROTTLE = "throttle"
    HTTP = "http"
    UNKNOWN = "unknown"
    SERVICE_UNAVAILABLE = "service_unavailable"


class ApiError(Exception):
    code: ErrorCode
    message: str

    def __init__(self, message: str, code: ErrorCode = ErrorCode.UNKNOWN):
        super().__init__(message, code)
        self.message = message
        self.code = code

    @property
    def status_code(self) -> int:
        return {
            ErrorCode.INVALID_REQUEST: status.HTTP_400_BAD_REQUEST,
            ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
            ErrorCode.THROTTLE: status.HTTP_429_TOO_MANY_REQUESTS,
            ErrorCode.HTTP: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCode.UNKNOWN: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }.get(self.code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApiResponse(BaseModel, Generic[DataItem, ErrorItem]):
    errors: Sequence[ErrorItem] = Field(default_factory=list)
    data: Sequence[DataItem] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str
    detail: Any = Field(default=None)
