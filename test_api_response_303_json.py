import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select
from src.database.models import Comprobante

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Comprobante).where(Comprobante.total == 28820.03))
        rows = result.scalars().all()
        
        output_data = []
        for r in rows:
            ruta_xml = r.ruta_resguardo or ""
            xml_exists = os.path.exists(ruta_xml) and os.path.isfile(ruta_xml) if ruta_xml else False
            pdf_exists = os.path.exists(ruta_xml.replace('.xml', '.pdf')) if ruta_xml and ruta_xml.endswith('.xml') else False

            from src.services.cfdi_storage import find_cfdi_attachments
            att = find_cfdi_attachments(str(r.uuid), r.serie or "", r.folio or "", r.tipo_comprobante or "I")
            
            fase1 = {"xml": xml_exists, "pdf": pdf_exists}
            
            if not xml_exists or not pdf_exists:
                 if not xml_exists and att["xml_path"]: xml_exists = True
                 if not pdf_exists and att["pdf_path"]: pdf_exists = True

            output_data.append({
                "folio": r.folio,
                "uuid": str(r.uuid),
                "ruta_resguardo": ruta_xml,
                "fase1": fase1,
                "att_xml": att["xml_path"],
                "att_pdf": att["pdf_path"],
                "fase3_xml_exists": xml_exists,
                "fase3_pdf_exists": pdf_exists
            })

        with open(r"c:\Test_Antigravity\Gestor_CFDI_Vantec\output_303_results.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output_data, indent=2))
        
        print("JSON Results saved.")

if __name__ == "__main__":
    asyncio.run(main())
