# backend/src/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from .entities import County, CountyStatistics, ProjectInfo

class DatabaseInterface(ABC):
    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[dict]:
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

class PdfServiceInterface(ABC):
    @abstractmethod
    def generate_pdf(self, template_name: str, context: dict) -> bytes:
        pass

class ProjectInfoServiceInterface(ABC):
    @abstractmethod
    def get_project_info(self) -> ProjectInfo:
        pass