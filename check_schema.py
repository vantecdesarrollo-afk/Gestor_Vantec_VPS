import asyncio
from src.database.session import engine
from sqlalchemy import text

async def check_schema():
    async with engine.connect() as conn:
        print("=== TABLES ===")
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in res]
        for t in tables:
            print(f"Table: {t}")
            count_res = await conn.execute(text(f"SELECT count(*) FROM {t}"))
            count = count_res.scalar()
            print(f"  Count: {count}")
        
        print("\n=== FOREIGN KEYS ON cfdis ===")
        fk_res = await conn.execute(text("""
            SELECT
                tc.table_name, kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='cfdis';
        """))
        for row in fk_res:
            print(f"FK: {row[1]} -> {row[2]}.{row[3]}")

if __name__ == "__main__":
    asyncio.run(check_schema())
