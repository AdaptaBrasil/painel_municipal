# backend/src/application/dependencies.py
from ..infrastructure.database import PostgresDatabase
from ..infrastructure.repository import CountyRepository, CountyStatisticsRepository, RiskFactorRepository
from ..infrastructure.pdf_service import PlaywrightPdfService
from ..infrastructure.project_info_service import TomlProjectInfoService
from ..infrastructure.image_service import HttpImageService
from ..domain.interfaces import ImageServiceInterface, PdfServiceInterface, ProjectInfoServiceInterface
from ..core.config import settings
from ..core.constants import PdfEngineType, ErrorKeys

def get_project_info_service() -> ProjectInfoServiceInterface:
    return TomlProjectInfoService()

def get_database() -> PostgresDatabase:
    return PostgresDatabase()


def get_county_repository() -> CountyRepository:
    db = get_database()
    return CountyRepository(db)

def get_county_statistics_repository() -> CountyStatisticsRepository:
    db = get_database()
    return CountyStatisticsRepository(db)

def get_risk_factor_repository() -> RiskFactorRepository:
    db = get_database()
    return RiskFactorRepository(db)


# Shared singleton so the icon download cache is reused across requests.
_image_service = HttpImageService()

def get_image_service() -> ImageServiceInterface:
    return _image_service


def get_pdf_service() -> PdfServiceInterface:
    """
    Factory method to decide which PDF engine to use based on configuration.
    Follows the Strategy Pattern.
    
    Future expansion: Add more PDF engines here as needed, e.g., WeasyPrint, Puppeteer, etc.    
    if settings.pdf_engine == PdfEngineType.WEASYPRINT:
        return WeasyPrintPdfService()
        
    if settings.pdf_engine == PdfEngineType.WKHTMLTOPDF:
        return WkHtmlToPdfService()
    
    if settings.pdf_engine == PdfEngineType.PUPPETEER:
        return PuppeteerPdfService()
    """
    
    if settings.pdf_engine == PdfEngineType.PLAYWRIGHT:
        return PlaywrightPdfService()
    
    print(f"Selected PDF Engine: {settings.pdf_engine}")
    
    

    raise ValueError(ErrorKeys.INVALID_PDF_ENGINE.value)