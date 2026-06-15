# backend/src/application/router.py
import io
import zipfile
from typing import List
###

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.config import settings
from ..core.constants import ErrorKeys
from ..domain.entities import County, CountyStatistics, RiskFactor, RiskFactorReport
from ..domain.interfaces import CountyStatisticsRepositoryInterface, CountyRepositoryInterface, ImageServiceInterface, PdfServiceInterface, ProjectInfoServiceInterface, RiskFactorRepositoryInterface
from .dependencies import get_county_repository, get_county_statistics_repository, get_pdf_service, get_project_info_service, get_risk_factor_repository

router = APIRouter(prefix="/api/v1")

# Initialize rate limiter with remote address as key function
limiter = Limiter(key_func=get_remote_address)


async def _embed_risk_icons(risks_record: List[dict], image_service: ImageServiceInterface) -> List[dict]:
    """Downloads each row's imageurl and embeds it as a base64 data URI in-place."""
    for row in risks_record:
        url = row.get("imageurl")
        if not url:
            continue
        data_uri = await image_service.fetch_as_data_uri(url)
        if data_uri:
            row["imageurl"] = data_uri
    return risks_record

@router.get("/database/status")
async def get_database_status(
    county_repo: CountyRepositoryInterface = Depends(get_county_repository)
):
    try:
        status = await county_repo.get_status_database()
        return {"database_status": "connected" if status else "disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Rate Limit Decorator: Max 1 ZIP per hour per IP (heavy operation)
@router.get("/reports/zip/all")
@limiter.limit("1/minute")
async def download_all_reports_zip(
    request: Request,
    county_repo: CountyRepositoryInterface = Depends(get_county_repository),
    county_statistic_repo: CountyStatisticsRepositoryInterface = Depends(get_county_statistics_repository),
    risk_factor_repo: RiskFactorRepositoryInterface = Depends(get_risk_factor_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service),
):
    counties = await county_repo.get_counties()
    if not counties:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Deixar o counties com somente 5 municípios para teste, depois retirar o slicing
        counties = counties[:20]  # --- IGNORE --- Remove this line to process all counties in production
        for county in counties:
            try:
                county_data = await county_repo.get_county(county.county_id)
                county_statistic_data = await county_statistic_repo.get_county_statistics(county.county_id)
                adapta_risks_data = await risk_factor_repo.get_risk_factors_by_county_id(county.county_id)
                adapta_main_factors_data = await risk_factor_repo.get_main_factors_by_county_id(county.county_id)

                if not all([county_data, county_statistic_data, adapta_risks_data, adapta_main_factors_data]):
                    print(f"Skipping county {county.county_id}: incomplete data")
                    continue

                risks_record = RiskFactorReport(risk_factors=adapta_risks_data).formatted_data_dict
                # risks_record = await _embed_risk_icons(risks_record, image_service)

                context = {
                    "county_record": county_data,
                    "county_statistic_record": county_statistic_data,
                    "main_factors_record": adapta_main_factors_data,
                    "risks_record": risks_record,
                    "pdf_engine": settings.pdf_engine,
                }

                pdf_bytes = await pdf_service.generate_pdf_merged(context)
                filename = f"{county_data.county_id}_{county_data.county}_Plano_Adaptacao.pdf"
                zf.writestr(filename, pdf_bytes)

            except Exception as e:
                print(f"Error generating PDF for county {county.county_id}: {e}")
                continue

    zip_buffer.seek(0)
    headers = {
        "Content-Disposition": 'attachment; filename="todos_municipios_Plano_Adaptacao.zip"'
    }
    return Response(content=zip_buffer.getvalue(), media_type="application/zip", headers=headers)


# Rate Limit Decorator: Max 2 PDFs per minute per IP!
@router.get("/reports/pdf/{county_id}")
@limiter.limit("20/minute")
async def download_report_pdf(
    request: Request,
    county_id: int,
    county_repo: CountyRepositoryInterface = Depends(get_county_repository),
    county_statistic_repo: CountyStatisticsRepositoryInterface = Depends(get_county_statistics_repository),
    risk_factor_repo: RiskFactorRepositoryInterface = Depends(get_risk_factor_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service),
):
    # Get all data needed for the report
    county_data = await county_repo.get_county(county_id)
    county_statistic_data = await county_statistic_repo.get_county_statistics(county_id)
    risk_factors_data = await risk_factor_repo.get_risk_factors_by_county_id(county_id)
    adapta_main_factors_data = await risk_factor_repo.get_main_factors_by_county_id(county_id)
    # Guard clause: No data found
    if not county_statistic_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_STATISTICS_NOT_FOUND.value)
    if not county_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)
    if not risk_factors_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.ADAPTA_RISKS_NOT_FOUND.value)
    if not adapta_main_factors_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.ADAPTA_MAIN_FACTORS_NOT_FOUND.value)

    # Prepare context for PDF generation
    county_record = county_data
    county_statistic_record = county_statistic_data
    main_factors_record = adapta_main_factors_data
    print("-----------------------")
    
    risk_factor_report = RiskFactorReport(risk_factors=risk_factors_data)

    # 3. Obter os dados processados na forma que preferir:

    # Opção A: Como uma lista de dicionários (preserva a ordem nativa e é ideal para APIs)
    dados_como_dict = risk_factor_report.formatted_data_dict

    # Baixa e embute (base64) cada ícone de risks_record[i].imageurl, para que
    # o PDF fique autocontido e os ícones sejam renderizados em boa qualidade.
    # dados_como_dict = await _embed_risk_icons(dados_como_dict, image_service)
    
    # Imprime a primeira linha completa com os os valores do dados_como_dict, para verificar a estrutura e os dados
    if dados_como_dict:
        print("\n--- Exemplo de linha do dados_como_dict ---")
        print(dados_como_dict[0])

    print("--- Formato Lista de Dicionários ---")
    # print(dados_como_dict)

    # Opção B: Como um DataFrame do Pandas (perfeito para manipulação ou exportação)
    df_formatado = risk_factor_report.formatted_data_df
    print("\n--- Formato DataFrame do Pandas ---")
    # print(df_formatado)


    
    context = {
        "county_record": county_record,
        "county_statistic_record": county_statistic_record,
        "main_factors_record": main_factors_record,
        "risks_record": dados_como_dict,
        "pdf_engine": settings.pdf_engine,
    }

    try:
        # Generates PDFs for each page separately and merges them
        pdf_bytes = await pdf_service.generate_pdf_merged(context)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": f'attachment; filename="{county_record.county_id}_{county_record.county}_Plano_Adaptacao.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


# Main factors 
@router.get("/counties/{county_id}/main-factors", response_model=List[RiskFactor])
async def get_main_factors(
    county_id: int,
    risk_factor_repo: RiskFactorRepositoryInterface = Depends(get_risk_factor_repository)
):
    try:
        return await risk_factor_repo.get_main_factors_by_county_id(county_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Main risks
@router.get("/counties/{county_id}/main-risks", response_model=List[RiskFactor])
async def get_main_risks(
    county_id: int,
    risk_factor_repo: RiskFactorRepositoryInterface = Depends(get_risk_factor_repository)
):
    try:
        return await risk_factor_repo.get_risk_factors_by_county_id(county_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))