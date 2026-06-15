import json

# backend/src/infrastructure/repository.py
from typing import List
from ..domain.interfaces import DatabaseInterface, CountyStatisticsRepositoryInterface, CountyRepositoryInterface, RiskFactorRepositoryInterface, LegendItemRepositoryInterface
from ..domain.entities import CountyStatistics, County, RiskFactor, LegendItem
from ..core.constants import ErrorKeys

class CountyRepository(CountyRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
    
    async def get_status_database(self) -> bool:
        return await self.db.test_connection()
    
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
        
class RiskFactorRepository(RiskFactorRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
    
    async def get_risk_factors_by_county_id(self, county_id: int) -> List[RiskFactor]:
            query = """
                select * from painel_municipal.quatro_pg_2 where county_id = $1 order by sep_id,risk, detail;
            """
            try:
                records = await self.db.fetch_all(query, county_id)
                
                
                if not records:
                    print("No records found for county_id:", county_id)  # Debugging line
                    raise Exception(ErrorKeys.RISK_FACTOR_NOT_FOUND.value)
                else:
                    print(f"Records found for county_id {county_id}: {len(records)}")  # Debugging line
                    # impirme 1 linha com key-value 
                    for record in records[:1]:  # Print only the first record for debugging
                        print("Sample record:", {key: record[key] for key in record.keys()})  # Debugging line
                    
                    
                return [RiskFactor(**record) for record in records]
            except Exception as e:
                raise Exception(str(e))
        
  
    async def get_main_factors_by_county_id(self, county_id: int) -> List[RiskFactor]:
        query = """
            SELECT DISTINCT sep_id, sep, imageurl 
            FROM painel_municipal.adapta_data 
            WHERE level = 2 AND county_id = $1 AND "year" = ' Ano Presente'; 
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                raise Exception(ErrorKeys.RISK_FACTOR_NOT_FOUND.value)
            return [RiskFactor(**record) for record in records]
        except Exception as e:
            raise Exception(str(e))
        
        
class LegendItemRepository(LegendItemRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_legend_items(self) -> List[LegendItem]:
        query = """
            SELECT * FROM adaptabrasil.legend_items li WHERE legend_id = 1 ORDER BY minvalue, maxvalue;
        """
        try:
            records = await self.db.fetch_all(query)
            return [LegendItem(**record) for record in records]
        except Exception:
            raise Exception(ErrorKeys.DATA_RETRIEVAL_FAILED.value)