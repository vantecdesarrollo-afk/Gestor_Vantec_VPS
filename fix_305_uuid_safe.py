import asyncio
import uuid
import os
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante
from src.services.cfdi_processor import CfdiProcessor
import glob

async def main():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    target_uuid = "af41872d-1e12-44ec-9d58-614b23e9655c"
    
    print(f"--- FIXING 305 BY UUID SAFE: {target_uuid} ---")
    try:
        async with AsyncSessionLocal() as session:
            # Set tenant for RLS
            await session.execute(
                text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                {"tid": entidad_id}
            )

            # Query by UUID
            query = select(Comprobante).where(Comprobante.uuid == target_uuid)
            result = await session.execute(query)
            comp = result.scalars().first()

            if comp:
                print(f"Found Comprobante: {comp.folio}, Ruta: {comp.ruta_resguardo}")
                if comp.ruta_resguardo:
                    all_xmls = glob.glob(os.path.join(comp.ruta_resguardo, "*.xml"))
                    files = [f for f in all_xmls if target_uuid.lower() in os.path.basename(f).lower()]
                    
                    if files:
                        xml_path = files[0]
                        print(f"Found XML File: {xml_path}")
                        processor = CfdiProcessor(session)
                        res_cfdi = await processor.procesar_cfdi(
                            ruta_archivo=xml_path,
                            entidad_id=uuid.UUID(entidad_id),
                            mover_a_boveda=False
                        )
                        print(f"✅ Processed successfully! New Total: {res_cfdi.total}")
                    else:
                        print("❌ XML NOT Found in list of files.")
            else:
                print("❌ Comprobante with UUID not found.")

            await session.commit()
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    print("--- END ---")

if __name__ == "__main__":
    asyncio.run(main())
