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
                query = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
                res = await conn.execute(query)
                results[table] = [dict(r._mapping) for r in res.all()]
            except Exception as e:
                results[table] = str(e)
    await engine.dispose()
    with open('full_diagnosis.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    asyncio.run(diagnose_full())
