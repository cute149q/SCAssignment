from enum import Enum
from typing import Any, Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

DataItem = TypeVar("DataItem", bound=BaseModel)
ErrorItem = TypeVar("ErrorItem", bound=BaseModel)


class ErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    THROTTLE = "throttle"
    HTTP = "http"
    UNKNOWN = "unknown"
    SERVICE_UNAVAILABLE = "service_unavailable"


class ApiError(BaseModel):
    code: str
    message: object


class ApiResponse(BaseModel, Generic[DataItem, ErrorItem]):
    errors: Sequence[ErrorItem] = Field(default_factory=list)
    data: Sequence[DataItem] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str
    detail: Any = Field(default=None)
