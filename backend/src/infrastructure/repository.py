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
            SELECT id, name, state, CONCAT(name, ' - ', state) AS display
            FROM adaptabrasil.county
            ORDER BY display;
        """
        try:
            records = await self.db.fetch_all(query)
            return [County(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)

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