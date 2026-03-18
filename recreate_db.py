import asyncio
from src.database.models import Base
from src.database.session import engine

async def recreate():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Recreating all tables based on v1.0.0 models...")
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Database recreated successfully.")

if __name__ == "__main__":
    asyncio.run(recreate())
