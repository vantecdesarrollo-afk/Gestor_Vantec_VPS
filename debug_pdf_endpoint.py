import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, cast, String
from src.database.models import Comprobante

async def debug_pdf():
    output = []
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Comprobante).where(Comprobante.folio.like('%804%')))
        comp = res.scalars().first()
        
        if not comp:
             output.append("No se encontró factura 804")
        else:
             uuid = str(comp.uuid)
             output.append(f"UUID: {uuid}")
             
             actual_path = comp.ruta_resguardo if comp and comp.ruta_resguardo else None
             output.append(f"1. actual_path (init): {actual_path}")
             
             if actual_path and os.path.exists(actual_path):
                 if os.path.isdir(actual_path):
                     actual_path = os.path.join(actual_path, f"{uuid}.pdf")
                 else:
                     actual_path = actual_path.replace('.xml', '.pdf')
             else:
                 actual_path = None
             output.append(f"2. actual_path (after replace): {actual_path}")

             if not actual_path or not os.path.exists(actual_path):
                 output.append("Path does not exist, looking in find_cfdi_attachments...")
                 from src.services.cfdi_storage import find_cfdi_attachments
                 att = find_cfdi_attachments(uuid, getattr(comp, 'serie', "") if comp else "", getattr(comp, 'folio', "") if comp else "", getattr(comp, 'tipo_comprobante', "I") if comp else "I")
                 output.append(f"att[pdf_path]: {att.get('pdf_path')}")
                 if att["pdf_path"]:
                      actual_path = att["pdf_path"]
             output.append(f"3. actual_path (after attachments): {actual_path}")

             if not actual_path or not os.path.exists(actual_path):
                  output.append("Triggering wkhtmltopdf block")
             else:
                  output.append(f"Skipping wkhtmltopdf block! PATH IS VALID: {actual_path}")

    with open("debug_pdf_endpoint_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Saved to debug_pdf_endpoint_output.txt")

if __name__ == "__main__":
    asyncio.run(debug_pdf())
