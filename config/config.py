#config/config.py
from typing import Optional
from pydantic import Field,SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    ###################################################
    project_prod:Optional[str]    = Field(default=None)
    project_qa:Optional[str]      = Field(default=None)
    url_p_automate:Optional[str]  = Field(default=None)

    ###################################################
    bigquery_sandbox_qa:Optional[str]  = Field(default=None)
    table_sandbox_qa:Optional[str]     = Field(default=None)
    table_sandbox_result:Optional[str] = Field(default=None)
    allowed_bq_tables:dict[str,str]    = Field(
        default_factory=lambda:{
                    "data_teams"    : "teams_validation_data",
                    "data_automate" : "response_validation_data"
        })
    ###################################################
    path_output:Path          = Path("data/")
    path_result:Path          = Path("data/")
    archivo_log: str = Field(default="app") #Field('log_ejecucion')
    ###################################################

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

print(settings)

