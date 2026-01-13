from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    project_prod:Optional[str]    = Field(default=None)
    project_qa:Optional[str]      = Field(default=None)
    url_p_automate:Optional[str]  = Field(default=None)
    path_output:Path              = Path("data/")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
