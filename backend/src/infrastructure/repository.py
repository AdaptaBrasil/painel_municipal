# backend/src/infrastructure/repository.py
from typing import List
from ..domain.interfaces import DatabaseInterface, CountyRepositoryInterface, TerritoryRepositoryInterface
from ..domain.entities import County, Territory
from ..core.constants import ErrorKeys

class CountyRepository(CountyRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db

    async def get_counties(self) -> List[County]:
        
        query = """
            SELECT DISTINCT county_id, county, state, CONCAT(county, ' - ', state) AS display FROM painel_municipal.adapta_data ORDER BY display;
        """
        try:
            records = await self.db.fetch_all(query)
            return [County(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)
        
    async def get_county(self, county_id: int) -> County:
        query = """
            SELECT id, county_id, gdp, area, idh, population FROM painel_municipal.county_data WHERE county_id = $1;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            return County(**records[0])
        except Exception as e:
            raise Exception(str(e))

class TerritoryRepository(TerritoryRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_territory(self, county_id: int) -> Territory:
        
        query = """
            SELECT id, county_id, county, state, region FROM painel_municipal.adapta_data WHERE county_id = $1
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.TERRITORY_NOT_FOUND.value)
            return Territory(**records[0])
        except Exception as e:
            raise Exception(str(e))