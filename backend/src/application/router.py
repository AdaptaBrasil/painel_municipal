# backend/src/application/router.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address


from typing import List
from .dependencies import get_county_repository, get_pdf_service
from ..domain.interfaces import CountyRepositoryInterface, PdfServiceInterface
from ..domain.entities import County
from ..core.constants import ErrorKeys

router = APIRouter(prefix="/api/v1")

# Initialize rate limiter with remote address as key function
limiter = Limiter(key_func=get_remote_address)

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

@router.get("/counties", response_model=List[County])
async def list_counties(
    repo: CountyRepositoryInterface = Depends(get_county_repository)
):
    try:
        return await repo.get_all_counties()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rate Limit Decorator: Max 2 PDFs per minute per IP!
@router.get("/reports/pdf/{county_id}")
@limiter.limit("2/minute")
async def download_report_pdf(
    request: Request,
    county_id: int,
    repo: CountyRepositoryInterface = Depends(get_county_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service)
):
    adaptation_data = await repo.get_data_by_county(county_id)
    county_data = await repo.get_county_by_id(county_id)
    
    # Guard clause: No data found
    if not adaptation_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)

    first_record = adaptation_data[0]
    context = {
        "county_name": first_record.county,
        "state": first_record.state,
        "region": first_record.region,
        "population": county_data.population if hasattr(county_data, 'population') else "N/A",
        "data": adaptation_data
    }

    try:
        # Apenas passamos o nome do arquivo, a configuração resolve o resto.
        pdf_bytes = pdf_service.generate_pdf("report_template.html", context)
    except Exception as e:
        # Imprime o erro real no console para debugar se der ruim
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": f'attachment; filename="Plano_Adaptacao_{first_record.county}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)