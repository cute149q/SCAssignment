from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    stage: str = Field(default="dev", validation_alias="STAGE")
    timer_db_endpoint: str = Field(..., validation_alias="TIMER_DB_ENDPOINT")
    timer_db_port: int = Field(..., validation_alias="TIMER_DB_PORT")
    timer_db_ssl_enabled: bool = Field(default=True, validation_alias="TIMER_DB_SSL_ENABLED")

    model_config = SettingsConfigDict(
        extra="allow",
        populate_by_name=True,
    )
