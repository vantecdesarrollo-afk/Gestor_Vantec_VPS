import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal

async def get_entidad():
    async with AsyncSessionLocal() as session:
        q = select(EntidadFiscal).where(EntidadFiscal.id == "e6f64bb0-3971-4cc8-b883-cd183eca77d7")
        res = await session.execute(q)
        ent = res.scalars().first()
        if ent:
             print(f"Entidad found: {ent.rfc} - {ent.razon_social}")
        else:
             print("Entidad NOT found")

if __name__ == "__main__":
    asyncio.run(get_entidad())
