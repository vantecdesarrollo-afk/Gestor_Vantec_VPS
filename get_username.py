import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import User

async def get_user():
    with open("username_out.txt", "w", encoding="utf-8") as f:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(User.username).limit(1))
            username = res.scalar()
            f.write(f"Username: {username}\n")

if __name__ == "__main__":
    asyncio.run(get_user())
