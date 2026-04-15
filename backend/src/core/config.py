# backend/src/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from .constants import PdfEngineType

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    
    # Nova variável para trocar o motor de PDF via .env
    pdf_engine: PdfEngineType = PdfEngineType.WEASYPRINT
    
    template_dir: Path = BACKEND_DIR / "src" / "static" / "report"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()