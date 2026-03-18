import asyncio
from src.database.session import engine
from sqlalchemy import text

async def sync():
    # ID real de VCO1307234VA
    ID = 'e6f64bb0-3971-4cc8-b883-cd183eca77d7'
    async with engine.begin() as conn:
        print(f"Sincronizando ID {ID} en tabla tenants...")
        await conn.execute(text(f"INSERT INTO tenants (id) VALUES ('{ID}') ON CONFLICT DO NOTHING"))
        print("Hecho.")

if __name__ == "__main__":
    asyncio.run(sync())
