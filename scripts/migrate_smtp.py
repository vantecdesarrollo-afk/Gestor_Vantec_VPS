import asyncio
from sqlalchemy import text
from src.database.session import engine
from src.database.models import Base

async def migrate():
    async with engine.begin() as conn:
        # Create the new table if it doesn't exist
        await conn.run_sync(Base.metadata.create_all)
        print("[+] Migración completada: Tabla 'entidad_smtp_configs' verificada.")

if __name__ == "__main__":
    asyncio.run(migrate())
