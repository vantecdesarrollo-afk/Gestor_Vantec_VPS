import asyncio
from src.database.session import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT id FROM tenants"))
            rows = res.all()
            with open("tenants_list.txt", "w") as f:
                for row in rows:
                    f.write(f"T: {row[0]}\n")
        except Exception as e:
            with open("tenants_list.txt", "w") as f:
                f.write(f"ERROR: {e}\n")

if __name__ == "__main__":
    asyncio.run(check())
