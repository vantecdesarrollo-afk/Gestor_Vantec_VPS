import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi

async def main():
    async with AsyncSessionLocal() as db:
         # find the last created CFDI inside table or top 5
         res = await db.execute(select(Cfdi).order_by(Cfdi.id.desc()).limit(5))
         rows = res.scalars().all()
         for r in rows:
              print(f"UUID: {r.uuid} | Folio: {getattr(r, 'folio', '')}")
              print(f"  xml: {r.xml_file_path}")
              print(f"  pdf: {r.pdf_file_path}\n")

if __name__ == "__main__":
    asyncio.run(main())
