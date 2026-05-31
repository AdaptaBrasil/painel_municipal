# backend/src/infrastructure/database.py
import asyncpg
from typing import List
from ..domain.interfaces import DatabaseInterface
from ..core.config import settings
from ..core.constants import ErrorKeys

class PostgresDatabase(DatabaseInterface):
    def __init__(self):
        # The class no longer needs internal SSL state as it will read from the singleton 'settings'
        pass

    async def _get_connection(self):
        """Centralizes the connection using the .env configuration"""
        return await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            ssl=settings.db_use_ssl,
            timeout=10.0
        )

    async def fetch_all(self, query: str, *args) -> List[dict]:
        try:
            conn = await self._get_connection()
            try:
                records = await conn.fetch(query, *args)
                return [dict(record) for record in records]
            finally:
                await conn.close()
        except Exception as e:
            print(f"DATABASE ERROR [fetch_all]: {type(e).__name__} -> {repr(e)}")
        
    async def test_connection(self) -> bool:
        try:
            conn = await self._get_connection()
            await conn.close()
            return True
        except Exception as e:
            print(f"ERRO AO TESTAR CONEXÃO: {type(e).__name__} -> {repr(e)}") 
            return False