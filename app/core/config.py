from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "genericmeds.db")

# On Vercel / serverless runtimes, copy sqlite DB to writable /tmp partition for optimal speed and reliability
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    import shutil
    tmp_db_path = "/tmp/genericmeds.db"
    if not os.path.exists(tmp_db_path) and os.path.exists(DEFAULT_DB_PATH):
        try:
            shutil.copyfile(DEFAULT_DB_PATH, tmp_db_path)
            DEFAULT_DB_PATH = tmp_db_path
        except Exception:
            pass
    elif os.path.exists(tmp_db_path):
        DEFAULT_DB_PATH = tmp_db_path


class Settings(BaseSettings):
    PROJECT_NAME: str = "GenericMeds AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini" | "mock"
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TIMEOUT_SECONDS: int = 20

    # Security
    ADMIN_API_KEY: str = "genericmeds-admin-key-supersecret-change-in-production"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    # Business Rules
    PRICE_STALE_DAYS: int = 90

    @field_validator("DATABASE_URL", mode="before")
    def resolve_sqlite_url(cls, v):
        if isinstance(v, str) and v.startswith("sqlite:///./"):
            rel_file = v.replace("sqlite:///./", "")
            return f"sqlite:///{os.path.join(BASE_DIR, rel_file)}"
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

