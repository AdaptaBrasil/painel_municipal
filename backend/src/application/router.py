# backend/src/application/router.py
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from .dependencies import get_county_repository, get_pdf_service
from ..domain.interfaces import CountyRepositoryInterface, PdfServiceInterface
from ..domain.entities import County
from ..core.constants import ErrorKeys

router = APIRouter(prefix="/api/v1")

@router.get("/counties", response_model=List[County])
async def list_counties(
    repo: CountyRepositoryInterface = Depends(get_county_repository)
):
    try:
        return await repo.get_all_counties()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/pdf/{county_id}")
async def download_report_pdf(
    county_id: int,
    repo: CountyRepositoryInterface = Depends(get_county_repository),
    pdf_service: PdfServiceInterface = Depends(get_pdf_service)
):
    adaptation_data = await repo.get_data_by_county(county_id)
    
    # Guard clause: No data found
    if not adaptation_data:
        raise HTTPException(status_code=404, detail=ErrorKeys.COUNTY_NOT_FOUND.value)

    first_record = adaptation_data[0]
    context = {
        "county_name": first_record.county,
        "state": first_record.state,
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