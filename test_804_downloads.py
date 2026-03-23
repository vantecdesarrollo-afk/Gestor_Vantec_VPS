import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select
from src.database.models import Comprobante

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Comprobante).where(Comprobante.folio.like('%804%')))
        rows = res.scalars().all()
        
        output = []
        if not rows:
            output.append("No se encontró factura 804 con LIKE")
        else:
            for r in rows:
                output.append(f"\n--- MATCH: {r.folio} ---")
                output.append(f"UUID: {r.uuid}")
                ruta_xml = r.ruta_resguardo or ""
                output.append(f"Ruta Resguardo (DB): {ruta_xml}")
                output.append(f"XML exists in DB path? {os.path.exists(ruta_xml)}")
                
                from src.services.cfdi_storage import find_cfdi_attachments
                att = find_cfdi_attachments(str(r.uuid), r.serie or "", r.folio or "", r.tipo_comprobante or "I")
                output.append(f"att[xml_path]: {att.get('xml_path')}")
                output.append(f"att[pdf_path]: {att.get('pdf_path')}")
                
                if att.get('xml_path'):
                     output.append(f"Actual XML exists? {os.path.exists(att['xml_path'])}")
                if att.get('pdf_path'):
                     output.append(f"Actual PDF exists? {os.path.exists(att['pdf_path'])}")

        with open("output_804.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print("Output saved to output_804.txt")

if __name__ == "__main__":
    asyncio.run(test())
