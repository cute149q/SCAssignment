from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SetTimerRequest(BaseModel):
    hours: int = Field(ge=0)
    minutes: int = Field(ge=0, le=59)
    seconds: int = Field(ge=0, le=59)
    url: HttpUrl


class GetTimerResponse(BaseModel):
    id: str
    seconds_remaining: int


class TimerTask(BaseModel):
    timer_id: str
    url: HttpUrl
    expires_at: datetime

    @property
    def id(self):
        return self.timer_id
