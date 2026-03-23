import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, Cfdi
from src.services.cfdi_storage import find_cfdi_attachments
from sqlalchemy import select, cast, String

async def test():
    db = AsyncSessionLocal()
    comp_q = select(Comprobante).where(cast(Comprobante.uuid, String) == 'D1D1F7D4-7683-4F46-A545-D8CA2E5E1A9C'.lower())
    comp = (await db.execute(comp_q)).scalar_one_or_none()
    print('COMP:', comp.folio if comp else None)
    
    cfdi_q = select(Cfdi).where(Cfdi.uuid == 'D1D1F7D4-7683-4F46-A545-D8CA2E5E1A9C'.upper())
    cfdi = (await db.execute(cfdi_q)).scalar_one_or_none()
    print('CFDI:', cfdi.folio if cfdi else None)

    folio = (comp.folio if comp else None) or (cfdi.folio if cfdi else None) or ""
    serie = (comp.serie if comp else None) or (cfdi.serie if cfdi else None) or ""
    att = find_cfdi_attachments('D1D1F7D4-7683-4F46-A545-D8CA2E5E1A9C', serie, folio, 'I')
    print('ATT:', att)
    
    await db.close()

if __name__ == '__main__':
    asyncio.run(test())
