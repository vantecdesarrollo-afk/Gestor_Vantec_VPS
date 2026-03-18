import asyncio
from sqlalchemy import text
from src.database.session import engine

async def migrate_smtp():
    async with engine.begin() as conn:
        print("🛠️ Applying SMTP Schema hotfix...")
        await conn.execute(text("ALTER TABLE entidad_smtp_configs ADD COLUMN IF NOT EXISTS from_email VARCHAR(255)"))
        print("✅ Column 'from_email' ensured.")

if __name__ == "__main__":
    asyncio.run(migrate_smtp())
