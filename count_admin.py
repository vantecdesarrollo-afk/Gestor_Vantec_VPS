import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import User
from sqlalchemy import select, func

async def test():
    with open("admin_count.log", "w", encoding="utf-8") as f:
        async with AsyncSessionLocal() as db:
            count = (await db.execute(select(func.count(User.user_id)).where(User.username == 'admin'))).scalar()
            f.write(f"✅ Total admin users: {count}\n")
            
            users = (await db.execute(select(User).where(User.username == 'admin'))).scalars().all()
            for u in users:
                 f.write(f" - ID: {u.user_id} | Email: {u.email} | Tenant: {u.tenant_id}\n")

if __name__ == "__main__":
    asyncio.run(test())
