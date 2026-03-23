import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, Cfdi
from sqlalchemy import select

async def m():
    db = AsyncSessionLocal()
    try:
        r = await db.execute(select(Comprobante).where(Comprobante.folio == '804'))
        item = r.scalars().first()
        if item:
            print(f"COMP: uuid={item.uuid}, folio={item.folio}, serie={item.serie}, ruta_resguardo={item.ruta_resguardo}")
        else:
            print("COMP: No encontrado con folio='804'")
            
        r2 = await db.execute(select(Cfdi).where(Cfdi.folio == '804'))
        cfdi = r2.scalars().first()
        if cfdi:
            print(f"CFDI: uuid={cfdi.uuid}, folio={cfdi.folio}, xml={cfdi.xml_file_path}, pdf={cfdi.pdf_file_path}")
        else:
            print("CFDI: No encontrado con folio='804'")
    except Exception as e:
        print("Err:", e)
    finally:
         await db.close()

if __name__ == '__main__':
    asyncio.run(m())
