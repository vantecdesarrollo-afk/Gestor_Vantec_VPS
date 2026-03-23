import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models_dashboard_opt import DashCfdiConcept
from sqlalchemy import select, func

async def m():
    db = AsyncSessionLocal()
    try:
        r = await db.execute(select(func.count()).select_from(DashCfdiConcept))
        print('CONCEPTS COUNT:', r.scalar())
    except Exception as e:
        print("Err:", e)
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(m())
