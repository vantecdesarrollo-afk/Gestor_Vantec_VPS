import asyncio
from sqlalchemy import text
from src.database.session import engine

async def check():
    async with engine.connect() as conn:
        for table in ['usuarios', 'entidades_fiscales', 'cfdis']:
            try:
                # PostgreSQL specific column inspection
                res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
                cols = [r[0] for r in res.all()]
                print(f"{table}: {cols}")
            except Exception as e:
                print(f"Error {table}: {e}")

if __name__ == "__main__":
    asyncio.run(check())
