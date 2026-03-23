import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def list_users():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        res = await db.execute(text("SELECT user_id, username, password_hash, is_active FROM users"))
        users = res.all()
        with open("users_clean.txt", "w", encoding="utf-8") as f:
            for u in users:
                f.write(f"ID: {u[0]} | Username: {u[1]} | Hash: {u[2]} | Active: {u[3]}\n")
        print("Written to users_clean.txt")
    except Exception as e:
         print("Error:", e)

if __name__ == "__main__":
    asyncio.run(list_users())
