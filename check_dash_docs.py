import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models_dashboard_opt import DashCfdiDocument
from sqlalchemy import select, func

async def check():
    async with AsyncSessionLocal() as db:
        cnt = await db.execute(select(func.count()).select_from(DashCfdiDocument))
        val = cnt.scalar()
        print(f"DashCfdiDocument count: {val}")

if __name__ == "__main__":
    asyncio.run(check())
