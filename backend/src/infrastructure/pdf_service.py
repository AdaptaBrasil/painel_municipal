# backend/src/infrastructure/pdf_service.py

import os
import io
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pypdf import PdfReader, PdfWriter
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
                pdf_config = dict(config)
                pdf_config.setdefault("prefer_css_page_size", True)
                pdf_bytes = await page.pdf(**pdf_config)
            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
            
            await browser.close()
            return pdf_bytes
    
    @staticmethod
    def _page_size_in_points(config: dict) -> tuple | None:
        """Converts the CSS pixel size used by Playwright (96 dpi) to PDF points (72 dpi)."""
        width, height = config.get("width"), config.get("height")
        if not (width and height):
            return None
        to_points = lambda css_px: float(str(css_px).removesuffix("px")) * 72 / 96
        return to_points(width), to_points(height)

    async def generate_pdf_merged(self, context: dict) -> bytes:
        """Generates PDFs for each page separately and then merges them."""
        pdf_writer = PdfWriter()

        # Iterates through each page defined in settings.pages_dir
        for page_config in settings.pages_dir:
            for page_path, config in page_config.items():

                if page_path.suffix.lower() == ".pdf":
                    # Static page already in PDF: appends it keeping its position,
                    # scaled to the same size as the rendered pages
                    if not page_path.exists():
                        raise FileNotFoundError(f"PDF not found: {page_path}")
                    target_size = self._page_size_in_points(config)
                    for page in PdfReader(str(page_path)).pages:
                        if target_size:
                            page.scale_to(*target_size)
                        pdf_writer.add_page(page)
                    continue

                # Generates the PDF for this page
                pdf_bytes = await self.generate_single_page_pdf(page_path, context, config)

                # Adds to the merger
                for page in PdfReader(io.BytesIO(pdf_bytes)).pages:
                    pdf_writer.add_page(page)

        # Writes the final PDF to memory
        output = io.BytesIO()
        pdf_writer.write(output)
        pdf_writer.close()

        output.seek(0)
        return output.getvalue()

    async def generate_pdf_page(self, context: dict, page_name: str) -> bytes:
        """Generates the PDF of a single report page identified by its directory name (e.g. 'pagina1')."""
        for page_config in settings.pages_dir:
            for page_path, config in page_config.items():
                if page_path.parent.name != page_name:
                    continue

                if page_path.suffix.lower() == ".pdf":
                    # Static page already in PDF: returns it scaled to the
                    # same size as the rendered pages
                    if not page_path.exists():
                        raise FileNotFoundError(f"PDF not found: {page_path}")
                    pdf_writer = PdfWriter()
                    target_size = self._page_size_in_points(config)
                    for page in PdfReader(str(page_path)).pages:
                        if target_size:
                            page.scale_to(*target_size)
                        pdf_writer.add_page(page)
                    output = io.BytesIO()
                    pdf_writer.write(output)
                    pdf_writer.close()
                    output.seek(0)
                    return output.getvalue()

                return await self.generate_single_page_pdf(page_path, context, config)

        raise KeyError(f"{ErrorKeys.PAGE_NOT_FOUND.value}: {page_name}")
   