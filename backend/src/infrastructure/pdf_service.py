# backend/src/infrastructure/pdf_service.py

import os

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
                # 'no-outline': None, 
                
                # Configurações de JavaScript
                'enable-javascript': '',   
                'javascript-delay': '1000', 
                
                # Tratamento de Rede e Arquivos
                'enable-local-file-access': '',
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore'
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
        
class PlaywrightPdfService(BasePdfService, PdfServiceInterface):
    async def generate_pdf(self, template_name: str, context: dict) -> bytes:
        from playwright.async_api import async_playwright
        import tempfile
        
        context["base_url"] = settings.template_dir.absolute().as_uri() + "/"
        print(f"Base URL for template: {context['base_url']}")  # Debugging line
        
        html_content = self.render_template(template_name, context)
        
        async with async_playwright() as p:
            # Mantemos as flags de segurança desligadas
            browser = await p.chromium.launch(args=[
                '--disable-web-security',
                '--allow-file-access-from-files'
            ])
            page = await browser.new_page()
            
            # 1. Cria um ficheiro HTML temporário fisicamente no disco do Docker
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(html_content)
                tmp_file_path = tmp_file.name
            
            # Define o conteúdo e aguarda o carregamento do DOM e execução do JS
            try:
                # 2. Usa o goto() em vez de set_content(). Agora a página tem permissão real!
                await page.goto(f"file://{tmp_file_path}", wait_until="networkidle")
            
                # Gera o PDF zerando as margens para "colar" o layout
                pdf_bytes = await page.pdf(
                    format="A3", 
                    print_background=True, 
                    landscape=False,
                    margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"} # <- ADICIONE ESTA LINHA
                )
            
            finally:
                # 4. Apaga o ficheiro temporário para não acumular lixo no disco do servidor
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
            
            await browser.close()
            return pdf_bytes

class PuppeteerPdfService(BasePdfService, PdfServiceInterface):
    async def generate_pdf(self, template_name: str, context: dict) -> bytes:
        import asyncio
        from pyppeteer import launch
        
        html_content = self.render_template(template_name, context)
        
        browser = await launch(args=['--no-sandbox'])
        page = await browser.newPage()
        await page.setContent(html_content, waitUntil="networkidle0")
        
        pdf_bytes = await page.pdf({'format': 'A4', 'printBackground': True})
        await browser.close()
        return pdf_bytes