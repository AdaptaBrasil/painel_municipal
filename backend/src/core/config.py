# backend/src/core/config.py
from typing import Dict, List
from enum import Enum

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
    
    class PageName(str, Enum):
        PAGE_00 = "pagina0"
        PAGE_01 = "pagina1"
        PAGE_02 = "pagina2"
        PAGE_03 = "pagina3"
        PAGE_04 = "pagina4"
        PAGE_05 = "pagina5"
        PAGE_06 = "pagina6"
        PAGE_07 = "pagina7"
        PAGE_08 = "pagina8" 
        
    # Records each page's template actually renders (see each pagina's index.html).
    # download_report_page_pdf uses this to skip database queries whose data would
    # never appear in the generated PDF. The climate projection query is still run
    # for every page because its geocode names the downloaded file.
    page_context_records: Dict[str, List[str]] = {
        PageName.PAGE_00.value: ["county_record"],
        PageName.PAGE_01.value: [],
        PageName.PAGE_02.value: ["county_record", "risks_record"],
        PageName.PAGE_03.value: ["county_record", "municipal_report_record"],
        PageName.PAGE_04.value: ["county_record", "municipal_resilience_profile_record"],
        PageName.PAGE_05.value: ["county_record", "climate_projection_record"],
        PageName.PAGE_06.value: ["county_record", "municipal_health_record"],
        PageName.PAGE_07.value: [],
        PageName.PAGE_08.value: [],
    }

    pages_dir: List[Dict[Path, dict]] = [
        {template_dir / PageName.PAGE_00.value / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_01.value / "file.pdf": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_02.value / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_03.value / "index.html": {"width": "842px", "height": "595px", "scale": 1.50, "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_04.value / "index.html": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_05.value / "index.html": {"width": "842px", "height": "595px", "scale": 1, "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_06.value / "index.html": {"width": "842px", "height": "595px", "scale": 1, "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_07.value / "file.pdf": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
        {template_dir / PageName.PAGE_08.value / "file.pdf": {"width": "842px", "height": "595px", "print_background": True, "landscape": False, "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}}},
    ]
    
    pyproject_path: Path = BACKEND_DIR / "pyproject.toml"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()