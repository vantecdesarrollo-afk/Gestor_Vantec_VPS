import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Hardcoded from .env for direct access
DATABASE_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"

async def diagnose():
    engine = create_async_engine(DATABASE_URL)
    print("🚀 VANTEC DIAGNOSTIC: Conectando a la DB directamente...")
    
    tables = ['usuarios', 'entidades_fiscales', 'cfdis']
    schema_map = {}
    
    async with engine.connect() as conn:
        for table in tables:
            try:
                res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
                cols = [r[0] for r in res.all()]
                schema_map[table] = cols
                print(f"Table {table}: {cols}")
            except Exception as e:
                print(f"Error inspecting {table}: {e}")
                
    await engine.dispose()
    
    with open('schema_diagnosis.json', 'w') as f:
        json.dump(schema_map, f, indent=4)
    print("\n✅ DIAGNOSTIC COMPLETO. Resultados en schema_diagnosis.json")

if __name__ == "__main__":
    asyncio.run(diagnose())
