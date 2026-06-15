# backend/src/core/config.py
from typing import Dict, List

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
    db_use_ssl: bool = False
    
    # New variable to switch the PDF engine via .env
    pdf_engine: PdfEngineType = PdfEngineType.PLAYWRIGHT
    
    template_dir: Path = BACKEND_DIR / "src" / "static" / "report"
    
    """
    width: 842px;
    height: 595px;
    """
    
    pages_dir: List[Dict[Path, dict]] = [
        {BACKEND_DIR / "src" / "static" / "report" / "pagina1" / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {BACKEND_DIR / "src" / "static" / "report" / "pagina2" / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        #{BACKEND_DIR / "src" / "static" / "report" / "pagina3" / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        #{BACKEND_DIR / "src" / "static" / "report" / "pagina5" / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
    ]
    
    pyproject_path: Path = BACKEND_DIR / "pyproject.toml"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()