import json

# backend/src/infrastructure/repository.py
from typing import List
from ..domain.interfaces import DatabaseInterface, MunicipalResilienceProfileRepositoryInterface, CountyRepositoryInterface, RiskFactorRepositoryInterface, MunicipalIndicatorsRepositoryInterface, ClimateProjectionRepositoryInterface
from ..domain.entities import County, RiskFactor, MunicipalIndicators, ClimateProjection
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
            if not records:
                print("--- No counties found")  # Debugging line
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            else:
                print(f"--- Counties found: {len(records)}")  # Debugging line
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
                print(f"--- No county found for county_id: {county_id}")  # Debugging line
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            else:
                print(f"--- County found for county_id {county_id}: {records[0]}")  # Debugging line
            if not records:
                raise Exception(ErrorKeys.COUNTY_NOT_FOUND.value)
            return County(**records[0])
        except Exception as e:
            raise Exception(str(e))
        
class RiskFactorRepository(RiskFactorRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
    
    async def get_risk_factors_by_county_id(self, county_id: int) -> List[RiskFactor]:
            query = """
                select * from painel_municipal.quatro_pg_2 where county_id = $1 order by current_value desc, sep_id, risk, detail;
            """
            try:
                records = await self.db.fetch_all(query, county_id)
                
                
                if not records:
                    print("--- No risk factors found for county_id:", county_id)  # Debugging line
                    raise Exception(ErrorKeys.RISK_FACTOR_NOT_FOUND.value)
                else:
                    print(f"--- Risk factors found for county_id {county_id}: {len(records)}")  # Debugging line
                    # impirme 1 linha com key-value 
                    # for record in records[:1]: print("Sample record:", {key: record[key] for key in record.keys()})  # Debugging line
                    
                    
                return [RiskFactor(**record) for record in records]
            except Exception as e:
                raise Exception(str(e))
        
class MunicipalIndicatorsRepository(MunicipalIndicatorsRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_municipal_report(self, county_id: int) -> MunicipalIndicators:
        query = """
            SELECT * FROM painel_municipal.pg_3 WHERE county_id = $1;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                print(f"--- No municipal report found for county_id: {county_id}")  # Debugging line
                raise Exception(ErrorKeys.MUNICIPAL_REPORT_NOT_FOUND.value)
            else:
                print(f"--- Municipal report found for county_id {county_id}: {len(records)}")  # Debugging line
            return MunicipalIndicators(**records[0])
        except Exception as e:
            raise Exception(str(e))
        
class MunicipalResilienceProfileRepository(MunicipalResilienceProfileRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_municipal_resilience_profile(self, county_id: int) -> dict:
        query = """
            SELECT * FROM painel_municipal.pq_4 WHERE county_id = $1;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                print(f"--- No municipal resilience profile found for county_id: {county_id}")  # Debugging line
                raise Exception(ErrorKeys.MUNICIPAL_RESILIENCE_PROFILE_NOT_FOUND.value)
            else:
                print(f"--- Municipal resilience profile found for county_id {county_id}: {len(records)}")  # Debugging line
            return dict(records[0])
        except Exception as e:
            raise Exception(str(e))
        
class ClimateProjectionRepository(ClimateProjectionRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
        
    async def get_climate_projection(self, county_id: int) -> ClimateProjection:
        query = """
            SELECT * FROM painel_municipal.pag5_climaticos_observados_cenarios WHERE county_id = $1;
        """
        try:
            records = await self.db.fetch_all(query, county_id)
            if not records:
                print(f"--- No climate projection found for county_id: {county_id}")  # Debugging line
                raise Exception(ErrorKeys.CLIMATE_PROJECTION_NOT_FOUND.value)
            else:
                print(f"--- Climate projection found for county_id {county_id}: {len(records)}")  # Debugging line
            return ClimateProjection(**records[0])
        except Exception as e:
            raise Exception(str(e))