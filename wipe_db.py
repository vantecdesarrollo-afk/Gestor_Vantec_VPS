
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "prueba01")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "gestor_cfdi")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def wipe_db():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Cleaning table cfdis...")
        await conn.execute(text("TRUNCATE TABLE cfdis CASCADE;"))
        
        print("Ensuring schema (parent_uuid)...")
        # Aseguramos que el UUID sea único para que la FK funcione si es necesario
        try:
            await conn.execute(text("ALTER TABLE cfdis ADD CONSTRAINT unique_uuid UNIQUE (uuid)"))
        except Exception as e:
            print(f"Note: unique_uuid constraint check: {e}")
            
        try:
            await conn.execute(text("ALTER TABLE cfdis ADD COLUMN IF NOT EXISTS parent_uuid VARCHAR(36)"))
            await conn.execute(text("ALTER TABLE cfdis ADD CONSTRAINT fk_parent_uuid FOREIGN KEY (parent_uuid) REFERENCES cfdis(uuid)"))
        except Exception as e:
            print(f"Note: Schema update note: {e}")
        
        print("Database ready for testing.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(wipe_db())
