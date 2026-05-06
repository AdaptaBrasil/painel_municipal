# backend/src/infrastructure/repository.py
from typing import List
from ..domain.interfaces import CountyRepositoryInterface, DatabaseInterface
from ..domain.entities import County, AdaptationData
from ..core.constants import ErrorKeys

class CountyRepository(CountyRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db

    async def get_all_counties(self) -> List[County]:
        
        query = """
            SELECT DISTINCT county_id, county, state, CONCAT(county, ' - ', state) AS display FROM painel_municipal.adapta_data ORDER BY display;
        """
        try:
            records = await self.db.fetch_all(query)
            return [County(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)
        
    async def get_county_by_id(self, county_id: int) -> County:
        query = """
            SELECT * FROM painel_municipal.county_data WHERE county_id = $1;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            return County(**records[0])
        except Exception as e:
            raise Exception(str(e))

    async def get_data_by_county(self, county_id: int) -> List[AdaptationData]:
        query = """
            SELECT id, sep_id, county_id, sep, county, microregion, 
                   mesoregion, state, region, imageurl, "year", 
                   color, "label", "order", value
            FROM painel_municipal.adapta_data 
            WHERE county_id = $1
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            return [AdaptationData(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)