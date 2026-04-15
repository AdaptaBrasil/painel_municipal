# backend/src/infrastructure/pdf_service.py
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from ..domain.interfaces import PdfServiceInterface
from ..core.config import settings
from ..core.constants import ErrorKeys

class WeasyPrintPdfService(PdfServiceInterface):
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(settings.template_dir)))

    def generate_pdf(self, template_name: str, context: dict) -> bytes:
        try:
            template = self.env.get_template(template_name)
            html_content = template.render(**context)
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except Exception as e:
            print(f"Jinja/Weasyprint Exception: {e}")
            raise Exception(ErrorKeys.PDF_GENERATION_FAILED.value)