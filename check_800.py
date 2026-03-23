import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, Cfdi
from src.services.cfdi_storage import find_cfdi_attachments
from sqlalchemy import select, cast, String

async def main():
    db = AsyncSessionLocal()
    c_q = select(Comprobante).where(Comprobante.folio == '800')
    c_res = await db.execute(c_q)
    c = c_res.scalar_one_or_none()
    
    cfdi_q = select(Cfdi).where(Cfdi.folio == '800')
    cfdi_res = await db.execute(cfdi_q)
    cf = cfdi_res.scalar_one_or_none()
    
    print("COMP:", c.uuid if c else None)
    print("CFDI:", cf.uuid if cf else None, cf.pdf_file_path if cf else None)
    
    uuid_str = c.uuid if c else (cf.uuid if cf else None)
    att = find_cfdi_attachments(str(uuid_str), 'PF', '800', 'I')
    print("ATTRIBUTES:", att)
    
if __name__ == "__main__":
    asyncio.run(main())
