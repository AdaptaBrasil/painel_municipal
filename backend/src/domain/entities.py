# backend/src/domain/entities.py
from pydantic import BaseModel
from typing import List, Optional

class County(BaseModel):
    id: int
    name: str
    state: str
    display: str

class AdaptationData(BaseModel):
    id: int
    sep_id: int
    county_id: int
    sep: str
    county: str
    microregion: str
    mesoregion: str
    state: str
    region: str
    imageurl: str
    year: str
    color: str
    label: str
    order: int
    value: float

class PdfReportData(BaseModel):
    county_name: str
    state: str
    adaptation_data: List[AdaptationData]