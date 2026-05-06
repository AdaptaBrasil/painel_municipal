# backend/src/domain/entities.py
from pydantic import BaseModel
from typing import List, Optional

class County(BaseModel):
    id: Optional[int] = None
    county_id: Optional[int] = None
    gdp: Optional[float] = None
    area: Optional[float] = None
    idh: Optional[float] = None
    population: Optional[int] = None
    
    @property
    def formatted_area(self) -> Optional[str]:
        if self.area is not None:
            return f"{self.area:.2f}"
        return None
    

class Territory(BaseModel):
    id: int
    county_id: int
    county: str
    state: str
    region: str

class PdfReportData(BaseModel):
    county_name: str
    state: str
    adaptation_data: List[Territory]

class ProjectInfo(BaseModel):
    name: str
    version: str
    description: str