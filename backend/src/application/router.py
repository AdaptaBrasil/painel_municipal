# backend/src/application/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.config import settings
from ..core.constants import ErrorKeys
from ..domain.entities import County, RiskFactorReport, MunicipalIndicatorsReport, MunicipalResilienceProfileReport, ClimateProjectionReport

from ..domain.interfaces import  PdfServiceInterface, ProjectInfoServiceInterface
from ..domain.interfaces import CountyRepositoryInterface, RiskFactorRepositoryInterface, MunicipalIndicatorsRepositoryInterface, MunicipalResilienceProfileRepositoryInterface, ClimateProjectionRepositoryInterface

from .dependencies import get_pdf_service, get_project_info_service
from .dependencies import get_county_repository, get_risk_factor_repository, get_municipal_report_repository, get_municipal_resilience_profile_repository, get_climate_projection_repository

router = APIRouter(prefix="/api/v1")

# Initialize rate limiter with remote address as key function
limiter = Limiter(key_func=get_remote_address)

@router.get("/health")
async def health_check(
    project_info_service: ProjectInfoServiceInterface = Depends(get_project_info_service),
    county_repo: CountyRepositoryInterface = Depends(get_county_repository)
):
    health_msg =  {"backend":{"status": "ok", "message": "Service is running"}}
    health_msg["pdf_engine"] = settings.pdf_engine
    health_msg["pages_dir"] = settings.pages_dir
    
    try:
        info_entity = project_info_service.get_project_info()
        health_msg.update({"project": info_entity.model_dump()})
    except Exception as e:
        print(f"Error reading project info: {e}")
        
    try:
        status = await county_repo.get_status_database()
        status_database = {"database_status": "connected" if status else "disconnected"}
        health_msg.update(status_database)
    except Exception as e:
        print(f"Error checking database status: {e}")
    
    
    return {**health_msg}

@router.get("/counties", response_model=List[County])
async def list_counties(
    repo: CountyRepositoryInterface = Depends(get_county_repository)
):
    try:
        return await repo.get_counties()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rate Limit Decorator: Max 200 PDFs per minute per IP!
@router.get("/reports/pdf/{county_id}")
@limiter.limit("200/minute")
async def download_report_pdf(
    request: Request,
    county_id: int,
    county_repo: CountyRepositoryInterface = Depends(get_county_repository),
    risk_factor_repo: RiskFactorRepositoryInterface = Depends(get_risk_factor_repository),
    municipal_report_repo: MunicipalIndicatorsRepositoryInterface = Depends(get_municipal_report_repository),
    municipal_resilience_profile_repo: MunicipalResilienceProfileRepositoryInterface = Depends(get_municipal_resilience_profile_repository),
    climate_projection_repo: ClimateProjectionRepositoryInterface = Depends(get_climate_projection_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service),
):
    # Prinjt initial log to confirm endpoint is hit
    print(f"---"*30)
    print(f"--- PDF Report Request ---")
    print(f"--- Received request for PDF report of county_id: {county_id} from IP: {request.client.host}")
    # Get all data needed for the report
    county_data = await county_repo.get_county(county_id)
    risk_factors_data = await risk_factor_repo.get_risk_factors_by_county_id(county_id)
    municipal_report_data = await municipal_report_repo.get_municipal_report(county_id)
    municipal_resilience_profile_data = await municipal_resilience_profile_repo.get_municipal_resilience_profile(county_id)
    climate_projection_data = await climate_projection_repo.get_climate_projection(county_id)
    # Guard clause: No data found
    if not county_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)
    if not risk_factors_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.RISK_FACTOR_NOT_FOUND.value)
    if not municipal_report_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.MUNICIPAL_REPORT_NOT_FOUND.value)
    if not municipal_resilience_profile_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.MUNICIPAL_RESILIENCE_PROFILE_NOT_FOUND.value)
    if not climate_projection_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.CLIMATE_PROJECTION_NOT_FOUND.value)

    # Prepare context for PDF generation
    county_record = county_data
    risk_factor_report = RiskFactorReport(risk_factors=risk_factors_data).formatted_data_dict
    municipal_report_record = MunicipalIndicatorsReport(municipal_indicators=municipal_report_data).formatted_data_dict
    municipal_resilience_profile_record = MunicipalResilienceProfileReport(municipal_resilience_profile=municipal_resilience_profile_data).formatted_data_dict
    climate_projection_record = ClimateProjectionReport(climate_projection=climate_projection_data).formatted_data_dict
    pure_climate_projection_record = ClimateProjectionReport(climate_projection=climate_projection_data).pure_data_dict
    
    # if municipal_resilience_profile_record: print(municipal_resilience_profile_record)
    # if pure_climate_projection_record: print(pure_climate_projection_record)

    context = {
        # Tables Data
        "county_record": county_record,
        "risks_record": risk_factor_report,
        "municipal_report_record": municipal_report_record,
        "municipal_resilience_profile_record": municipal_resilience_profile_record,
        "climate_projection_record": climate_projection_record,

        # Config Data
        "pdf_engine": settings.pdf_engine,
    }

    try:
        # Generates PDFs for each page separately and merges them
        pdf_bytes = await pdf_service.generate_pdf_merged(context)
        print(f"--- PDF Report Generated ---")
        print(f"--- Successfully generated PDF for county_id: {county_id}, sending response...")
    except Exception as e:
        print(f"Error generating PDF: {ErrorKeys.PDF_GENERATION_FAILED.value} {e}")
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": f'attachment; filename="{county_record.county_id}_{county_record.county}_Plano_Adaptacao.pdf"'
    }
    print(f"---"*30)
    print("\n\n")


    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)