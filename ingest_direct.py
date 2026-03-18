import asyncio
import os
import uuid
import defusedxml.ElementTree as ET
from datetime import datetime
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi, Tenant
from sqlalchemy import select

async def ingest():
    files = [r'c:\Vantec\Test\factura_ingreso.xml', r'c:\Vantec\Test\pago_rep.xml']
    
    async with AsyncSessionLocal() as db:
        tenant = (await db.execute(select(Tenant).where(Tenant.rfc == 'VCO1307234VA'))).scalar_one_or_none()
        if not tenant:
             print("Tenant not found")
             return
        tenant_id = tenant.tenant_id

        for fpath in files:
            if not os.path.exists(fpath):
                print(f"Skipping {fpath}")
                continue
            with open(fpath, 'rb') as f:
                content = f.read()

            root = ET.fromstring(content)
            namespaces = {
                'cfdi': root.tag.split('}')[0].strip('{'),
                'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
            }
            version = root.get('Version') or root.get('version')
            fecha_str = root.get('Fecha') or root.get('fecha')
            total_str = root.get('Total') or root.get('total')
            
            emisor = root.find('.//cfdi:Emisor', namespaces)
            rfc_emisor = emisor.get('Rfc') if emisor is not None else None
            
            receptor = root.find('.//cfdi:Receptor', namespaces)
            rfc_receptor = receptor.get('Rfc') if receptor is not None else None
            
            tfd = root.find('.//tfd:TimbreFiscalDigital', namespaces)
            cfdi_uuid = tfd.get('UUID') if tfd is not None else str(uuid.uuid4())

            fecha_dt = datetime.fromisoformat(fecha_str)

            new_cfdi = Cfdi(
                tenant_id=tenant_id,
                uuid=cfdi_uuid,
                rfc_emisor=rfc_emisor,
                rfc_receptor=rfc_receptor,
                issue_date=fecha_dt,
                total=float(total_str) if total_str else 0.0,
                version=version,
                xml_file_path=fpath,
                status='VALID'
            )
            db.add(new_cfdi)
        await db.commit()
    print("Ingest success")

if __name__ == "__main__":
    asyncio.run(ingest())
