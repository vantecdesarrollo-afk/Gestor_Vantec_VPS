
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "prueba01")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "gestor_cfdi")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def check_entity():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id, rfc FROM entidades_fiscales WHERE id = 'e6f64bb0-3971-4cc8-b883-cd183eca77d7'"))
        row = res.fetchone()
        if row:
            print(f"Found entity: {row[0]} | {row[1]}")
        else:
            print("Entity not found!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_entity())
