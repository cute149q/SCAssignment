from pydantic import BaseModel, field_validator, Field


class SetTimerRequest(BaseModel):
    hours: int = Field(ge=0)
    minutes: int = Field(ge=0, le=59)
    seconds: int = Field(ge=0, le=59)
    url: str

    @field_validator("url")
    def validate_url(cls, value):
        if not value.startswith("http"):
            raise ValueError("URL must start with http")
        return value


class GetTimerResponse(BaseModel):
    id: str
    seconds_left: int
