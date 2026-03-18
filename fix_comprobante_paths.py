import asyncio
import uuid
import os
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante
from src.services.cfdi_processor import CfdiProcessor
from datetime import datetime

async def fix():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    output = []
    try:
        async with AsyncSessionLocal() as session:
            # Set tenant for RLS
            await session.execute(
                text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                {"tid": entidad_id}
            )
            
            # 1. Update paths for ALL Comprobantes to match storage/tenants/...
            output.append("Updating paths...")
            q_all = select(Comprobante)
            res_all = await session.execute(q_all)
            comprobantes = res_all.scalars().all()
            
            updated_count = 0
            for c in comprobantes:
                 if c.fecha_emision:
                      year = str(c.fecha_emision.year)
                      month = f"{c.fecha_emision.month:02d}"
                      # Use pure relative or correct format
                      new_path = os.path.join(os.getcwd(), "storage", "tenants", entidad_id, year, month)
                      if c.ruta_resguardo != new_path:
                           c.ruta_resguardo = new_path
                           updated_count += 1
                           
            output.append(f"Updated paths for {updated_count} comprobantes.")

            # 2. Fix Folio 303 using CfdiProcessor
            output.append("\nFixing Folio 303 via CfdiProcessor...")
            target_uuid = "d2a9308b-f4d9-4357-8adf-de186a7ef5d1"
            xml_file_path = os.path.join(
                os.getcwd(), "storage", "tenants", entidad_id, "2025", "10", 
                "D2A9308B-F4D9-4357-8ADF-DE186A7EF5D1.xml"
            )
            
            if os.path.exists(xml_path := xml_file_path):
                 output.append(f"Found XML File: {xml_path}")
                 processor = CfdiProcessor(session)
                 # procesar_cfdi handles upsert and relations
                 # entidad_id must be UUID type
                 res_cfdi = await processor.procesar_cfdi(
                     ruta_archivo=xml_path,
                     entidad_id=uuid.UUID(entidad_id),
                     mover_a_boveda=False
                 )
                 output.append(f"Cfdi processed successfully! UUID: {res_cfdi.uuid}, Total: {res_cfdi.total}")
                 
                 # Also update Comprobante.total in case it's 0 to match
                 q_303 = select(Comprobante).where(Comprobante.uuid == uuid.UUID(target_uuid))
                 res_303 = await session.execute(q_303)
                 comp_303 = res_303.scalars().first()
                 if comp_303:
                      comp_303.total = res_cfdi.total
                      output.append(f"Updated Comprobante total to {comp_303.total}")
            else:
                 output.append(f"XML File NOT Found at {xml_file_path}")

            await session.commit()
            output.append("\nDone.")

    except Exception as e:
        output.append(f"\n❌ EXCEPTION: {str(e)}")

    with open("fix_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(fix())
