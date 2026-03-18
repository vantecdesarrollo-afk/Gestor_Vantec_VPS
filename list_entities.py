import asyncio
import sys
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal, Cfdi
from sqlalchemy import select, func

async def check():
    try:
        async with AsyncSessionLocal() as db:
            print("--- BUSCANDO ENTIDADES ---")
            sys.stdout.flush()
            res = await db.execute(select(EntidadFiscal))
            entities = res.scalars().all()
            for e in entities:
                print(f"ENTITY: {e.rfc} | {e.id} | {e.razon_social}")
                sys.stdout.flush()
            
            print("--- BUSCANDO HUERFANOS ---")
            sys.stdout.flush()
            res = await db.execute(select(func.count(Cfdi.cfdi_id)).where(Cfdi.entidad_id == None))
            count = res.scalar()
            print(f"HUERFANOS: {count}")
            sys.stdout.flush()
    except Exception as ex:
        print(f"ERROR: {ex}")
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(check())
