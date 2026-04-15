# backend/src/application/dependencies.py
from ..infrastructure.database import PostgresDatabase
from ..infrastructure.repository import CountyRepository
from ..infrastructure.pdf_service import WeasyPrintPdfService

def get_database() -> PostgresDatabase:
    return PostgresDatabase()

def get_county_repository() -> CountyRepository:
    db = get_database()
    return CountyRepository(db)

def get_pdf_service() -> WeasyPrintPdfService:
    return WeasyPrintPdfService()