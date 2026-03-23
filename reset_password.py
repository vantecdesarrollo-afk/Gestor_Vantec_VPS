import asyncio
from passlib.context import CryptContext
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User))
        users = res.scalars().all()
        if not users:
            print("No users found")
            return
            
        for user in users:
            print(f"Resetting password for: {user.username}")
            user.password_hash = pwd_context.hash("prueba01")
        
        await db.commit()
        print("All passwords reset to: prueba01")

if __name__ == "__main__":
    asyncio.run(reset())
