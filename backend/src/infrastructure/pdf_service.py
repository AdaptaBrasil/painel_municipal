# backend/src/infrastructure/pdf_service.py
import pdfkit
from weasyprint import HTML
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
            # options can be expanded for footer/header in the future
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }
            # False as second argument returns the PDF as bytes
            return pdfkit.from_string(html_content, False, options=options)
        except Exception as e:
            print(f"WkHtmlToPdf Exception: {e}")
            raise Exception(ErrorKeys.PDF_GENERATION_FAILED.value)