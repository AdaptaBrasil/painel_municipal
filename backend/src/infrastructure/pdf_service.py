# backend/src/infrastructure/pdf_service.py

from jinja2 import Environment, FileSystemLoader
from ..domain.interfaces import PdfServiceInterface
from ..core.config import settings
from ..core.constants import ErrorKeys

class BasePdfService:
    """Base class to handle Jinja2 template rendering."""
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(settings.template_dir)))

    def render_template(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

class WeasyPrintPdfService(BasePdfService, PdfServiceInterface):
    def generate_pdf(self, template_name: str, context: dict) -> bytes:
        # Lazy import: Only loads WeasyPrint if this strategy is actively used
        try:
            from weasyprint import HTML
        except ImportError as e:
            print("WeasyPrint is not installed or missing system libraries: ", e)
            raise Exception(ErrorKeys.PDF_GENERATION_FAILED.value)

        try:
            html_content = self.render_template(template_name, context)
            return HTML(string=html_content).write_pdf()
        except Exception as e:
            print(f"WeasyPrint Exception: {e}")
            raise Exception(ErrorKeys.PDF_GENERATION_FAILED.value)

class WkHtmlToPdfService(BasePdfService, PdfServiceInterface):
    def generate_pdf(self, template_name: str, context: dict) -> bytes:
        try:
            html_content = self.render_template(template_name, context)
            
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }
            
            # Lazy import: Only loads pdfkit if this strategy is actively used
            try:
                import pdfkit
            except ImportError as e:
                print("pdfkit is not installed or wkhtmltopdf is not available: ", e)
                raise Exception(ErrorKeys.PDF_GENERATION_FAILED.value)
            
            
            return pdfkit.from_string(html_content, False, options=options)
        except Exception as e:
            print(f"WkHtmlToPdf Exception: {e}")
            raise Exception(ErrorKeys.PDF_GENERATION_FAILED.value) 