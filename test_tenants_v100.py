import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import Tenant
from sqlalchemy import select

async def test():
    async with AsyncSessionLocal() as db:
        tenants = (await db.execute(select(Tenant))).scalars().all()
        print(f"✅ Total Tenants: {len(tenants)}")
        for t in tenants:
             print(f" - ID: {t.tenant_id} | RFC: {t.rfc} | Name: {t.business_name}")

if __name__ == "__main__":
    asyncio.run(test())
