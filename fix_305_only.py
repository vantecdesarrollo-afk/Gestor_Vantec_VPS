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
    print("--- FIX 305 ONLY ---")
    try:
        async with AsyncSessionLocal() as session:
            # Set tenant for RLS
            await session.execute(
                text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                {"tid": entidad_id}
            )

            query = select(Comprobante).where(Comprobante.folio == '305')
            result = await session.execute(query)
            comp = result.scalars().first()

            if comp:
                print(f"Found Folio 305, UUID: {comp.uuid}, Ruta: {comp.ruta_resguardo}")
                if comp.ruta_resguardo:
                    files = glob.glob(os.path.join(comp.ruta_resguardo, f"*{comp.uuid}*.xml"))
                    if files:
                        xml_path = files[0]
                        print(f"Found XML: {xml_path}")
                        processor = CfdiProcessor(session)
                        res_cfdi = await processor.procesar_cfdi(
                            ruta_archivo=xml_path,
                            entidad_id=uuid.UUID(entidad_id),
                            mover_a_boveda=False
                        )
                        print(f"✅ Processed 305! New Total: {res_cfdi.total}")
                    else:
                        print("❌ XML NOT Found")
            else:
                print("❌ Folio 305 not found in DB.")

            await session.commit()
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    print("--- END ---")

if __name__ == "__main__":
    asyncio.run(main())
