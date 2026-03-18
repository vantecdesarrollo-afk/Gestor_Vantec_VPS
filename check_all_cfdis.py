import asyncio
import os
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal, Cfdi
from sqlalchemy import select

async def check():
    output = []
    try:
        async with AsyncSessionLocal() as db:
            output.append("--- ALL ENTITIES ---")
            res = await db.execute(select(EntidadFiscal))
            entities = res.scalars().all()
            for e in entities:
                output.append(f"E: {e.id} | {e.rfc} | {e.razon_social}")
            
            output.append("\n--- ALL CFDIS (TOP 10) ---")
            res = await db.execute(select(Cfdi).limit(10))
            for c in res.scalars().all():
                output.append(f"C: {c.cfdi_id} | E_ID: {c.entidad_id} | RFC: {c.rfc_emisor}->{c.rfc_receptor}")
            
            res = await db.execute(select(Cfdi).where(Cfdi.entidad_id == None))
            orphans = res.scalars().all()
            output.append(f"\nTOTAL ORPHANS: {len(orphans)}")
    except Exception as ex:
        output.append(f"ERROR: {ex}")

    with open("check_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(check())
