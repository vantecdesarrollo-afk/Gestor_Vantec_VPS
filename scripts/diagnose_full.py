import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"

async def diagnose_full():
    engine = create_async_engine(DATABASE_URL)
    results = {}
    
    async with engine.connect() as conn:
        for table in ['usuarios', 'entidades_fiscales', 'cfdis']:
            try:
                # Get columns and types
                query = text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                res = await conn.execute(query)
                cols = [{"name": r[0], "type": r[1], "nullable": r[2]} for r in res.all()]
                results[table] = cols
            except Exception as e:
                print(f"Error {table}: {e}")
                
    await engine.dispose()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(diagnose_full())
