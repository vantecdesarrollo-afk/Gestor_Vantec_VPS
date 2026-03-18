import asyncio
from src.database.session import engine
from sqlalchemy import text

async def inspect_columns():
    async with engine.connect() as conn:
        res = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tenants'
        """))
        cols = [f"{row[0]} ({row[1]})" for row in res]
        with open("tenants_cols.txt", "w") as f:
            f.write("\n".join(cols))

if __name__ == "__main__":
    asyncio.run(inspect_columns())
