
import asyncio
import os
import sys

# Añadir el path del proyecto para importar src
sys.path.append(os.getcwd())

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings

async def get_id():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT id, nombre FROM entidades_fiscales LIMIT 1'))
        row = res.fetchone()
        if row:
            print(f"ID: {row[0]}")
            print(f"NOMBRE: {row[1]}")
        else:
            print("NOTFOUND")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(get_id())
