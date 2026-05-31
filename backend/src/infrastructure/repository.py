import json

# backend/src/infrastructure/repository.py
from typing import List
from ..domain.interfaces import DatabaseInterface, CountyStatisticsRepositoryInterface, CountyRepositoryInterface, AdaptaDataRepositoryInterface, LegendItemRepositoryInterface
from ..domain.entities import CountyStatistics, County, AdaptaData, LegendItem
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
        
class AdaptaDataRepository(AdaptaDataRepositoryInterface):
    def __init__(self, db: DatabaseInterface):
        self.db = db
    
    async def get_main_risks_by_county_id(self, county_id: int) -> List[AdaptaData]:
            query = """
            
            SELECT 
                s.name AS sep_name,
                i.id AS id_risco,
                i.name AS risco,
                i.legend_id,
                round(cast(v2.value AS numeric), 2) AS risco_valor,
                
                -- en: Creates dynamic columns as keys of a JSON
                jsonb_object_agg(
                    replace(
                        CASE 
                            WHEN position('Ameaça' in i2.name) > 0 THEN 'Ameaça'
                            ELSE i2.name 
                        END, ' ', '_'
                    ),
                    round(cast(v.value AS numeric), 2)
                ) AS dimensions_json

            FROM adaptabrasil."indicator" i 
            INNER JOIN adaptabrasil.sep s ON s.id = i.sep_id 
            INNER JOIN adaptabrasil.indicator_indicator ii ON ii.indicator_id_master = i.id
            INNER JOIN adaptabrasil."indicator" i2 ON ii.indicator_id_detail = i2.id
            INNER JOIN adaptabrasil.value v ON v.indicator_id = i2.id 
                AND v."year" < 2026 
                AND v.geoobject_id = $1
            INNER JOIN adaptabrasil.value v2 ON v2.indicator_id = i.id
                AND v2."year" < 2026 
                AND v2.geoobject_id = $1
            WHERE i.level = 2 AND s.painel_municipal AND i.id <> 10024
            GROUP BY 
                s.name, 
                i.id, 
                i.name, 
                i.legend_id, 
                round(cast(v2.value AS numeric), 2)
            ORDER BY risco_valor DESC, sep_name, risco;

            """
            try:
                records = await self.db.fetch_all(query, county_id)
                mapping_records = []
                
                if not records:
                    print("No records found for county_id:", county_id)  # Debugging line
                    raise Exception(ErrorKeys.ADAPTA_DATA_NOT_FOUND.value)
                else:
                    print(f"Records found for county_id {county_id}: {len(records)}")  # Debugging line
                    print("Size of records:", len(records))  # Debugging line
                    # Imprimir a primeira linhas para verificar os nomes das colunas
                    print("First record in records:", records[0])  # Debugging line
                    print("Column names BEFORE mapping in records:", records[0].keys())  # Debugging line
                    
                    for record in records:
                        dimensions_json = record.get("dimensions_json", {})
                        if isinstance(dimensions_json, str):
                            dimensions_json = json.loads(dimensions_json)  # Convert string to dictionary
                        
                        new_record = {
                            "sep_name": record.get("sep_name"),
                            "risk_id": record.get("id_risco"),
                            "risk_name": record.get("risco"),
                            "risk_value": record.get("risco_valor"),
                            "threat": dimensions_json.get("Ameaça"),
                            "exposure": dimensions_json.get("Exposição"),
                            "vulnerability": dimensions_json.get("Vulnerabilidade"),
                            
                        }
                        mapping_records.append(new_record)
                    print("Column names AFTER mapping in new_records:", mapping_records[0].keys())
                    print("First record in records:", mapping_records[0])  # Debugging line

                    
                return [AdaptaData(**record) for record in mapping_records]
            except Exception as e:
                raise Exception(str(e))
        
    async def get_main_risks_by_county_id_old(self, county_id: int) -> List[AdaptaData]:
        query = """
            SELECT id, sep_id, county_id, sep, risk, county, microregion, mesoregion, state, region, imageurl, "level", "year", color, "label", "order", value
            FROM painel_municipal.adapta_data
            WHERE "level" = 2 and county_id = $1 and "year" = ' Ano Presente' order by "value" desc;
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