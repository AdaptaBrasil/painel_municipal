# backend/src/domain/entities.py
from pydantic import BaseModel
from typing import List, Optional

from ..helpers.common.formatting.number_formatting_processing import NumberFormattingProcessing

class County(BaseModel):
    county_id: int
    county: str
    state: str
    region: str
    display: Optional[str] = None
    
class CountyStatistics(BaseModel):
    id: Optional[int] = None
    county_id: Optional[int] = None
    gdp: Optional[float] = None
    area: Optional[float] = None
    idh: Optional[float] = None
    population: Optional[int] = None
    
    @property
    def formatted_area(self) -> Optional[str]:
        formatted_value = None
        if self.area is not None:
            truncated_value = NumberFormattingProcessing.to_decimal_truncated(self.area, value_to_ignore=None, precision=2)
            formatted_value = NumberFormattingProcessing.format_number_brazilian(float(truncated_value))
        return formatted_value
    
    @property
    def formatted_population(self) -> Optional[str]:
        formatted_value = None
        if self.population is not None:
            formatted_value = NumberFormattingProcessing.format_number_brazilian(self.population)
        return formatted_value

class PdfReportData(BaseModel):
    county_name: str
    state: str
    adaptation_data: List[County]

class ProjectInfo(BaseModel):
    name: str
    version: str
    description: str