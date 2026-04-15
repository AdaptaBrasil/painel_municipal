# backend/src/core/constants.py
from enum import Enum

class PdfEngineType(str, Enum):
    WEASYPRINT = "weasyprint"
    WKHTMLTOPDF = "wkhtmltopdf"
    
class ErrorKeys(str, Enum):
    DB_CONNECTION_FAILED = "ERR_DB_CONNECTION_FAILED"
    COUNTY_NOT_FOUND = "ERR_COUNTY_NOT_FOUND"
    DATA_RETRIEVAL_FAILED = "ERR_DATA_RETRIEVAL_FAILED"
    PDF_GENERATION_FAILED = "ERR_PDF_GENERATION_FAILED"