from pydantic import Field
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    timer_db_endpoint: str = Field(..., validation_alias="TIMER_DB_ENDPOINT")
    timer_db_port: int = Field(..., validation_alias="TIMER_DB_PORT")
    timer_db_ssl_enabled: bool = Field(default=True, validation_alias="TIMER_DB_SSL_ENABLED")