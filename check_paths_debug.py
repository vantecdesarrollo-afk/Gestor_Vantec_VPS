import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi

async def main():
    with open("/tmp/ruta_paths.txt", "w") as f:
         async with AsyncSessionLocal() as db:
              res = await db.execute(select(Cfdi).limit(5))
              rows = res.scalars().all()
              for r in rows:
                   f.write(f"UUID: {r.uuid}\n")
                   f.write(f"  xml_file_path: {r.xml_file_path}\n")
                   f.write(f"  pdf_file_path: {r.pdf_file_path}\n\n")

if __name__ == "__main__":
    asyncio.run(main())
