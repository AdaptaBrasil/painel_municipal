# backend/src/infrastructure/repository.py
from typing import List
from ..domain.interfaces import DatabaseInterface, CountyStatisticsRepositoryInterface, CountyRepositoryInterface, AdaptaDataRepositoryInterface
from ..domain.entities import CountyStatistics, County, AdaptaData
from ..core.constants import ErrorKeys

class CountyStatisticsRepository(CountyStatisticsRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db

    async def get_counties_statistics(self) -> List[CountyStatistics]:
        
        query = """
            SELECT DISTINCT county_id, county, state, CONCAT(county, ' - ', state) AS display FROM painel_municipal.adapta_data ORDER BY display;
        """
        try:
            records = await self.db.fetch_all(query)
            return [CountyStatistics(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)
        
    async def get_county_statistics(self, county_id: int) -> CountyStatistics:
        query = """
            SELECT id, county_id, gdp, area, idh, population FROM painel_municipal.county_data WHERE county_id = $1;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            return CountyStatistics(**records[0])
        except Exception as e:
            raise Exception(str(e))

class CountyRepository(CountyRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_counties(self) -> List[County]:
        query = """
            SELECT  distinct county_id, county, region, state, CONCAT(county, ' - ', state) AS display FROM painel_municipal.adapta_data ORDER BY display;
        """
        try:
            records = await self.db.fetch_all(query)
            return [County(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)

    async def get_county(self, county_id: int) -> County:
        query = """
            SELECT  distinct county_id, county, region, state, CONCAT(county, ' - ', state) AS display FROM painel_municipal.adapta_data WHERE county_id = $1 ORDER BY display;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            return County(**records[0])
        except Exception as e:
            raise Exception(str(e))
        
class AdaptaDataRepository(AdaptaDataRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_main_risks_by_county_id(self, county_id: int) -> List[AdaptaData]:
        query = """
            SELECT id, sep_id, county_id, sep, risk, county, microregion, mesoregion, state, region, imageurl, "level", "year", color, "label", "order", value
            FROM painel_municipal.adapta_data
            WHERE "level" = 2 and county_id = $1 and "year" = ' Ano Presente';
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.ADAPTA_DATA_NOT_FOUND.value)
            return [AdaptaData(**record) for record in records]
        except Exception as e:
            raise Exception(str(e))
        
    async def get_main_factors_by_county_id(self, county_id: int) -> List[AdaptaData]:
        query = """
            SELECT DISTINCT sep_id, sep, imageurl 
            FROM painel_municipal.adapta_data 
            WHERE level = 2 AND county_id = $1 AND "year" = ' Ano Presente'; 
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.ADAPTA_DATA_NOT_FOUND.value)
            return [AdaptaData(**record) for record in records]
        except Exception as e:
            raise Exception(str(e))