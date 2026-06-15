# backend/src/infrastructure/image_service.py
import base64
import mimetypes
from typing import Dict, Optional

import httpx

from ..domain.interfaces import ImageServiceInterface


class HttpImageService(ImageServiceInterface):
    """Downloads remote images and embeds them as base64 data URIs.

    Embedding the bytes directly into the HTML avoids relying on network
    access (or CORS) at PDF-render time and guarantees the icons shown in
    risks_record are actually baked into the generated PDF.
    """

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        # In-memory cache: the same icon URL is typically reused across
        # several rows/counties, so we only download it once per process.
        self._cache: Dict[str, Optional[str]] = {}

    async def fetch_as_data_uri(self, url: str) -> Optional[str]:
        if not url:
            return None

        if url in self._cache:
            return self._cache[url]

        data_uri = await self._download(url)
        self._cache[url] = data_uri
        return data_uri

    async def _download(self, url: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.content

                content_type = response.headers.get("content-type")
                if not content_type or "/" not in content_type:
                    content_type = mimetypes.guess_type(url)[0] or "application/octet-stream"
                content_type = content_type.split(";")[0].strip()

                encoded = base64.b64encode(content).decode("ascii")
                return f"data:{content_type};base64,{encoded}"
        except Exception as e:
            print(f"Error downloading image '{url}': {e}")
            return None
