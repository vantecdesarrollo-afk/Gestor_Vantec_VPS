import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(EntidadFiscal))
        entities = res.scalars().all()
        for e in entities:
            print(f"RFC: {e.rfc} | ID: {e.id}")

if __name__ == "__main__":
    asyncio.run(check())
