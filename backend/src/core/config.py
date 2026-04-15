# backend/src/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# __file__ = config.py -> parent = core -> parent = src -> parent = backend
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    
    # Atualizado para o novo caminho correto
    template_dir: Path = BACKEND_DIR / "src" / "static" / "report"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()