import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"
engine = create_async_engine(DATABASE_URL)

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'comprobantes'"))
        cols = [row[0] for row in res.all()]
        print(f"COLS:{','.join(cols)}")

if __name__ == "__main__":
    asyncio.run(run())
