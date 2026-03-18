import asyncio
from sqlalchemy import text
from src.database.session import engine

async def migrate_smtp_enterprise():
    async with engine.begin() as conn:
        print("🛠️ Applying SMTP Enterprise Schema Refactoring...")
        await conn.execute(text("ALTER TABLE entidad_smtp_configs RENAME COLUMN use_tls TO _use_tls_deprecated"))
        await conn.execute(text("ALTER TABLE entidad_smtp_configs ADD COLUMN IF NOT EXISTS security_type VARCHAR(50) DEFAULT 'STARTTLS'"))
        await conn.execute(text("ALTER TABLE entidad_smtp_configs ADD COLUMN IF NOT EXISTS authentication_type VARCHAR(50) DEFAULT 'LOGIN'"))
        
        # from_email was already added in the previous step, but let's rename it if it exists
        try:
            await conn.execute(text("ALTER TABLE entidad_smtp_configs RENAME COLUMN from_email TO from_address"))
            print("✅ from_email renamed to from_address")
        except Exception as e:
            print("ℹ️ from_address might already exist or from_email doesn't exist.")
            
        print("✅ Enterprise Schema Applied.")

if __name__ == "__main__":
    asyncio.run(migrate_smtp_enterprise())
