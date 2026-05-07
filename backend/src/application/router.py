# backend/src/application/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.constants import ErrorKeys
from ..domain.entities import County, CountyStatistics, AdaptaData
from ..domain.interfaces import CountyStatisticsRepositoryInterface, CountyRepositoryInterface, PdfServiceInterface, ProjectInfoServiceInterface, AdaptaDataRepositoryInterface
from .dependencies import get_county_repository, get_county_statistics_repository, get_pdf_service, get_project_info_service, get_adapta_data_repository

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
    county_repo: CountyRepositoryInterface = Depends(get_county_repository),
    county_statistic_repo: CountyStatisticsRepositoryInterface = Depends(get_county_statistics_repository),
    adapta_data_repo: AdaptaDataRepositoryInterface = Depends(get_adapta_data_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service)
):
    # Get all data needed for the report
    county_data = await county_repo.get_county(county_id)
    county_statistic_data = await county_statistic_repo.get_county_statistics(county_id)
    adapta_risks_data = await adapta_data_repo.get_main_risks_by_county_id(county_id)
    adapta_main_factors_data = await adapta_data_repo.get_main_factors_by_county_id(county_id)
    # Guard clause: No data found
    if not county_statistic_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_STATISTICS_NOT_FOUND.value)
    if not county_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)
    if not adapta_risks_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.ADAPTA_RISKS_NOT_FOUND.value)
    if not adapta_main_factors_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.ADAPTA_MAIN_FACTORS_NOT_FOUND.value)

    # Prepare context for PDF generation
    county_record = county_data
    county_statistic_record = county_statistic_data
    main_factors_record = adapta_main_factors_data
    risks_record = adapta_risks_data
    
    context = {
        "county_record": county_record,
        "county_statistic_record": county_statistic_record,
        "main_factors_record": main_factors_record,
        "risks_record": risks_record
    }

    try:
        pdf_bytes = pdf_service.generate_pdf("report_template.html", context)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": f'attachment; filename="{county_record.county_id}_{county_record.county}_Plano_Adaptacao.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


# Principais fatores 
@router.get("/counties/{county_id}/main-factors", response_model=List[AdaptaData])
async def get_main_factors(
    county_id: int,
    adapta_data_repo: AdaptaDataRepositoryInterface = Depends(get_adapta_data_repository)
):
    try:
        return await adapta_data_repo.get_main_factors_by_county_id(county_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Principais riscos
@router.get("/counties/{county_id}/main-risks", response_model=List[AdaptaData])
async def get_main_risks(
    county_id: int,
    adapta_data_repo: AdaptaDataRepositoryInterface = Depends(get_adapta_data_repository)
):
    try:
        return await adapta_data_repo.get_main_risks_by_county_id(county_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))