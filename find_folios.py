import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi
from sqlalchemy import select

async def find_folios():
    folios = ["305", "804", "800"]
    async with AsyncSessionLocal() as db:
        for f in folios:
            print(f"\n--- Checking Folio {f} ---")
            query = select(Cfdi).where(Cfdi.folio == f)
            res = await db.execute(query)
            cfdis = res.scalars().all()
            if not cfdis:
                print(f"Folio {f} not found.")
                continue
            for c in cfdis:
                print(f"UUID: {c.uuid}")
                print(f"Type: {c.tipo_comprobante}")
                print(f"Total: {c.total}")
                print(f"XML: {c.xml_file_path}")
                print(f"PDF: {c.pdf_file_path}")

if __name__ == "__main__":
    asyncio.run(find_folios())
