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

async def count_cfdis():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT count(*) FROM cfdis"))
            count = res.scalar()
            res2 = await conn.execute(text("SELECT uuid, tenant_id FROM cfdis"))
            rows = res2.all()
            with open("cfdis_count.txt", "w") as f:
                 f.write(f"Count: {count}\n")
                 for r in rows:
                      f.write(f"UUID: {r[0]} | Tenant: {r[1]}\n")
            print(f"Successfully counted: {count}")
        except Exception as e:
            with open("cfdis_count.txt", "w") as f:
                f.write(f"ERROR: {e}\n")
            print(f"Error: {e}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(count_cfdis())
