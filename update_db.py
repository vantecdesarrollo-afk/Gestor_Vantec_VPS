import asyncio
from sqlalchemy import text
from src.database.session import engine

async def sync():
    async with engine.begin() as conn:
        print("Sincronizando columnas faltantes...")
        await conn.execute(text("ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS estatus_sat VARCHAR(20);"))
        await conn.execute(text("ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS ruta_resguardo VARCHAR(500);"))
        print("✅ Columnas sincronizadas.")

if __name__ == "__main__":
    asyncio.run(sync())