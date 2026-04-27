# backend/src/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from .entities import County, AdaptationData, ProjectInfo

class DatabaseInterface(ABC):
    @abstractmethod
    async def fetch_all(self, query: str, *args) -> List[dict]:
        pass

class CountyRepositoryInterface(ABC):
    @abstractmethod
    async def get_all_counties(self) -> List[County]:
        pass
    
    @abstractmethod
    async def get_county_by_id(self, county_id: int) -> County:
        pass

    @abstractmethod
    async def get_data_by_county(self, county_id: int) -> List[AdaptationData]:
        pass

class PdfServiceInterface(ABC):
    @abstractmethod
    def generate_pdf(self, template_name: str, context: dict) -> bytes:
        pass

class ProjectInfoServiceInterface(ABC):
    @abstractmethod
    def get_project_info(self) -> ProjectInfo:
        pass