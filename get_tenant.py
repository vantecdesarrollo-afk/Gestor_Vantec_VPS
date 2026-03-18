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

async def get_tenant():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT tenant_id, business_name FROM tenants"))
            rows = res.all()
            with open("tenants_list_custom.txt", "w") as f:
                for row in rows:
                    f.write(f"ID: {row[0]} | Name: {row[1]}\n")
            print("Successfully fetched tenants.")
        except Exception as e:
            with open("tenants_list_custom.txt", "w") as f:
                f.write(f"ERROR: {e}\n")
            print(f"Error fetching tenants: {e}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(get_tenant())
