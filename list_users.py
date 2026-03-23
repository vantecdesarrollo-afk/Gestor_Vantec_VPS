import asyncio
from src.database.session import get_db
from src.database.models import User
from sqlalchemy import select

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def list_users():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    result = await db.execute(select(User))
    users = result.scalars().all()
    for u in users:
        print(f"User: {u.username}, Email: {u.email}, Superadmin: {getattr(u, 'is_superadmin', False)}")

if __name__ == "__main__":
    asyncio.run(list_users())
