import asyncio
from sqlalchemy import text
from src.database.session import engine

async def repair():
    async with engine.begin() as conn:
        print("🚀 Sincronizando columnas faltantes...")
        queries = [
            "ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS nombre_emisor VARCHAR(255);",
            "ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS nombre_receptor VARCHAR(255);",
            "ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(10);",
            "ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS forma_pago VARCHAR(2);",
            "ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS status VARCHAR(20);"
        ]
        for q in queries:
            await conn.execute(text(q))
        print("✅ Columnas sincronizadas con éxito.")

if __name__ == "__main__":
    asyncio.run(repair())