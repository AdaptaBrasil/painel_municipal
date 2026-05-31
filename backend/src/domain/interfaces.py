# backend/src/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from .entities import County, CountyStatistics, AdaptaData,  ProjectInfo, LegendItem


class LegendItemRepositoryInterface(ABC):
    @abstractmethod
    async def get_legend_items(self) -> List[LegendItem]:
        pass

class DatabaseInterface(ABC):
    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[dict]:
        pass
    @abstractmethod
    async def test_connection(self) -> bool:
        pass

class CountyStatisticsRepositoryInterface(ABC):
    @abstractmethod
    async def get_counties_statistics(self) -> List[CountyStatistics]:
        pass
    
    @abstractmethod
    async def get_county_statistics(self, county_id: int) -> CountyStatistics:
        pass
    
class CountyRepositoryInterface(ABC):
    @abstractmethod
    async def get_counties(self) -> List[County]:
        pass
    
    @abstractmethod
    async def get_county(self, county_id: int) -> County:
        pass
    
class AdaptaDataRepositoryInterface(ABC):
    @abstractmethod
    async def get_main_risks_by_county_id(self, county_id: int) -> List[AdaptaData]:
        pass
    
    # get_main_factors_by_county_id
    @abstractmethod
    async def get_main_factors_by_county_id(self, county_id: int) -> List[AdaptaData]:
        pass

class PdfServiceInterface(ABC):
    @abstractmethod
    async def generate_single_page_pdf(self, page_path: Path, context: dict, config: dict) -> bytes:
        pass
    
    @abstractmethod
    async def generate_pdf_merged(self, context: dict) -> bytes:
        pass

class ProjectInfoServiceInterface(ABC):
    @abstractmethod
    def get_project_info(self) -> ProjectInfo:
        pass