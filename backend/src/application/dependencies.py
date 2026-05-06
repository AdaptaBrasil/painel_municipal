# backend/src/application/dependencies.py
from ..infrastructure.database import PostgresDatabase
from ..infrastructure.repository import CountyRepository, TerritoryRepository
from ..infrastructure.pdf_service import WeasyPrintPdfService, WkHtmlToPdfService
from ..infrastructure.project_info_service import TomlProjectInfoService
from ..domain.interfaces import PdfServiceInterface, ProjectInfoServiceInterface
from ..core.config import settings
from ..core.constants import PdfEngineType, ErrorKeys

def get_project_info_service() -> ProjectInfoServiceInterface:
    return TomlProjectInfoService()

def get_database() -> PostgresDatabase:
    return PostgresDatabase()

def get_county_repository() -> CountyRepository:
    db = get_database()
    return CountyRepository(db)

def get_territory_repository() -> CountyRepository:
    db = get_database()
    return TerritoryRepository(db)

def get_pdf_service() -> PdfServiceInterface:
    """
    Factory method to decide which PDF engine to use based on configuration.
    Follows the Strategy Pattern.
    """
    print(f"Selected PDF Engine: {settings.pdf_engine}")
    if settings.pdf_engine == PdfEngineType.WKHTMLTOPDF:
        return WkHtmlToPdfService()
    
    if settings.pdf_engine == PdfEngineType.WEASYPRINT:
        return WeasyPrintPdfService()
        
    raise ValueError(ErrorKeys.INVALID_PDF_ENGINE.value)