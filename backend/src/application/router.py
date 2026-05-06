# backend/src/application/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.constants import ErrorKeys
from ..domain.entities import County
from ..domain.interfaces import CountyRepositoryInterface, TerritoryRepositoryInterface, PdfServiceInterface, ProjectInfoServiceInterface
from .dependencies import get_county_repository, get_pdf_service, get_project_info_service, get_territory_repository

router = APIRouter(prefix="/api/v1")

# Initialize rate limiter with remote address as key function
limiter = Limiter(key_func=get_remote_address)

@router.get("/health")
async def health_check(
    project_info_service: ProjectInfoServiceInterface = Depends(get_project_info_service)
):
    health_msg =  {"status": "ok", "message": "Service is running"}
    project_info = {}
    try:
        info_entity = project_info_service.get_project_info()
        project_info = {"project": info_entity.model_dump()}
    except Exception as e:
        print(f"Error reading project info: {e}")
        
    return {**health_msg, **project_info}

@router.get("/counties", response_model=List[County])
async def list_counties(
    repo: CountyRepositoryInterface = Depends(get_county_repository)
):
    try:
        return await repo.get_counties()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rate Limit Decorator: Max 2 PDFs per minute per IP!
@router.get("/reports/pdf/{county_id}")
@limiter.limit("2/minute")
async def download_report_pdf(
    request: Request,
    county_id: int,
    territory_repo: TerritoryRepositoryInterface = Depends(get_territory_repository),
    county_repo: CountyRepositoryInterface = Depends(get_county_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service)
):
    # Get all data needed for the report
    county_data = await county_repo.get_county(county_id)
    territory_data = await territory_repo.get_territory(county_id)
    
    # Guard clause: No data found
    if not territory_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)
    if not county_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)

    # Prepare context for PDF generation
    territory_record = territory_data
    county_record = county_data
    
    context = {
        "territory_record": territory_record,
        "county_record": county_record,
    }

    try:
        pdf_bytes = pdf_service.generate_pdf("report_template.html", context)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": f'attachment; filename="Plano_Adaptacao_{territory_record.county}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)