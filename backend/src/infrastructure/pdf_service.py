# backend/src/infrastructure/pdf_service.py

import os
import io
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pypdf import PdfMerger
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

class PlaywrightPdfService(BasePdfService, PdfServiceInterface):
    async def generate_single_page_pdf(self, page_path: Path, context: dict, config: dict) -> bytes:
        """Generates a PDF for a specific page with its configuration."""
        from playwright.async_api import async_playwright
        import tempfile
        
        # Uses the page-specific configuration
        # print(f"Config: {config}")  # Debugging line
        
        base_dir_path = page_path.parent  # This will give us the directory containing the template
        template_name = page_path.name  # This will give us the template file name (e.g., "index.html")
        
        # Renders the page template
        context["base_url"] = base_dir_path.absolute().as_uri() + "/"
        
        template_file = page_path
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")
        
        # Uses the loader with the page-specific directory
        page_env = Environment(loader=FileSystemLoader(str(base_dir_path)))
        template = page_env.get_template(template_name)
        html_content = template.render(**context)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=[
                '--disable-web-security',
                '--allow-file-access-from-files'
            ])
            page = await browser.new_page(device_scale_factor=3)
              
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(html_content)
                tmp_file_path = tmp_file.name
            
            try:
                await page.goto(f"file://{tmp_file_path}", wait_until="networkidle")
                
                # Uses the page-specific configuration
                pdf_bytes = await page.pdf(**config)
            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
            
            await browser.close()
            return pdf_bytes
    
    async def generate_pdf_merged(self, context: dict) -> bytes:
        """Generates PDFs for each page separately and then merges them."""
        pdf_merger = PdfMerger()
        
        # Iterates through each page defined in settings.pages_dir
        for page_config in settings.pages_dir:
            for page_path, config in page_config.items():
                
                # Generates the PDF for this page
                pdf_bytes = await self.generate_single_page_pdf(page_path, context, config)
                
                # Adds to the merger
                pdf_file = io.BytesIO(pdf_bytes)
                pdf_merger.append(pdf_file)
        
        # Writes the final PDF to memory
        output = io.BytesIO()
        pdf_merger.write(output)
        pdf_merger.close()
        
        output.seek(0)
        return output.getvalue()
   