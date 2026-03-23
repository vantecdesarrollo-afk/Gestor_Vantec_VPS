import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, Cfdi
from sqlalchemy import select, cast, String, func
from src.services.cfdi_storage import find_cfdi_attachments

async def m():
    db = AsyncSessionLocal()
    try:
        # Folio 800 uuid val (search with folio to get uuid first)
        r = await db.execute(select(Comprobante).where(Comprobante.folio.like('%800%')))
        item = r.scalars().first()
        if not item:
             print("Comprobante 800 No encontrado en DB")
             return
             
        uuid_str = str(item.uuid).upper()
        print(f"800 UUID_STR: {uuid_str}")
        
        r2 = await db.execute(select(Cfdi).where(func.lower(Cfdi.uuid) == uuid_str.lower()))
        cfdi = r2.scalars().first()
        
        comp = item
        my_serie = getattr(comp, 'serie', "") if comp else getattr(cfdi, 'serie', "")
        my_folio = getattr(comp, 'folio', "") if comp else getattr(cfdi, 'folio', "")
        my_tipo = getattr(comp, 'tipo_comprobante', "I") if comp else getattr(cfdi, 'tipo_comprobante', "I")

        print(f"PARAMS: serie='{my_serie}', folio='{my_folio}', tipo='{my_tipo}'")
        
        att = find_cfdi_attachments(uuid_str, my_serie, my_folio, my_tipo)
        print(f"ATT FIND: {att}")
        
    except Exception as e:
        print("Err:", e)
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(m())
