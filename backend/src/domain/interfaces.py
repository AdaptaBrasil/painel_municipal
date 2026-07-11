# backend/src/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from .entities import County, RiskFactor,  ProjectInfo, MunicipalIndicators, MunicipalResilienceProfile, ClimateProjection


class DatabaseInterface(ABC):
    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[dict]:
        pass
    @abstractmethod
    async def test_connection(self) -> bool:
        pass

class CountyRepositoryInterface(ABC):
    @abstractmethod
    async def get_counties(self) -> List[County]:
        pass
    
    @abstractmethod
    async def get_county(self, county_id: int) -> County:
        pass

class MunicipalIndicatorsRepositoryInterface(ABC):
    @abstractmethod
    async def get_municipal_report(self, county_id: int) -> MunicipalIndicators:
        pass
    
# class para MunicipalResilienceProfile
class MunicipalResilienceProfileRepositoryInterface(ABC):
    @abstractmethod
    async def get_municipal_resilience_profile(self, county_id: int) -> MunicipalResilienceProfile:
        pass
# class para ClimateProjection
class ClimateProjectionRepositoryInterface(ABC):
    @abstractmethod
    async def get_climate_projection(self, county_id: int) -> ClimateProjection:
        pass
    
class RiskFactorRepositoryInterface(ABC):
    @abstractmethod
    async def get_risk_factors_by_county_id(self, county_id: int) -> List[RiskFactor]:
        pass
    
class PdfServiceInterface(ABC):
    @abstractmethod
    async def generate_single_page_pdf(self, page_path: Path, context: dict, config: dict) -> bytes:
        pass
    
    @abstractmethod
    async def generate_pdf_merged(self, context: dict) -> bytes:
        pass

    @abstractmethod
    async def generate_pdf_page(self, context: dict, page_name: str) -> bytes:
        pass

class ProjectInfoServiceInterface(ABC):
    @abstractmethod
    def get_project_info(self) -> ProjectInfo:
        pass

class ImageServiceInterface(ABC):
    @abstractmethod
    async def fetch_as_data_uri(self, url: str) -> Optional[str]:
        """Downloads an image and returns it as a base64 data URI, or None on failure."""
        pass