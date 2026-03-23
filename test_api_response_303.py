import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, text
from src.database.models import Comprobante

async def main():
    async with AsyncSessionLocal() as db:
        print("Consultando API simulada para Folio 303...")
        
        result = await db.execute(select(Comprobante).where(Comprobante.total == 28820.03))
        rows = result.scalars().all()
        
        if not rows:
             print("No se encontraron comprobantes con total 28820.03.")
             return

        for r in rows:
            print(f"\n--- COMPROBANTE Folio: {r.folio} UUID: {r.uuid} ---")
            ruta_xml = r.ruta_resguardo or ""
            xml_exists = os.path.exists(ruta_xml) and os.path.isfile(ruta_xml) if ruta_xml else False
            pdf_exists = os.path.exists(ruta_xml.replace('.xml', '.pdf')) if ruta_xml and ruta_xml.endswith('.xml') else False

            print(f"Ruta Resguardo: {ruta_xml}")
            print(f"xml_exists (Fase 1): {xml_exists}")
            print(f"pdf_exists (Fase 1): {pdf_exists}")

            from src.services.cfdi_storage import find_cfdi_attachments
            att = find_cfdi_attachments(str(r.uuid), r.serie or "", r.folio or "", r.tipo_comprobante or "I")
            print(f"att['xml_path']: {att['xml_path']}")
            print(f"att['pdf_path']: {att['pdf_path']}")
            
            if not xml_exists and att["xml_path"]:
                 xml_exists = True
            if not pdf_exists and att["pdf_path"]:
                 pdf_exists = True

            print(f"xml_exists (Fase 3): {xml_exists}")
            print(f"pdf_exists (Fase 3): {pdf_exists}")

if __name__ == "__main__":
    asyncio.run(main())
