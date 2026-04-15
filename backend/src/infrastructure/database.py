# backend/src/infrastructure/database.py
import asyncpg
from typing import List
from ..domain.interfaces import DatabaseInterface
from ..core.config import settings
from ..core.constants import ErrorKeys

class PostgresDatabase(DatabaseInterface):
    def __init__(self):
        self.dsn = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    async def fetch_all(self, query: str, *args) -> List[dict]:
        try:
            conn = await asyncpg.connect(self.dsn)
            records = await conn.fetch(query, *args)
            await conn.close()
            return [dict(record) for record in records]
        except Exception as e:
            # In a real scenario, log the exception 'e' here
            raise Exception(ErrorKeys.DB_CONNECTION_FAILED.value)