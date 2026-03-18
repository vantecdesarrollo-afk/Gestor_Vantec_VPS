import asyncio
import uuid
import os
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Cfdi
from src.services.cfdi_processor import CfdiProcessor
import glob

async def main():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    target_uuid = "af41872d-1e12-44ec-9d58-614b23e9655c"
    
    with open("reprocess_305_output.txt", "w", encoding="utf-8") as f_out:
        f_out.write(f"--- FIXING 305 SAFE LOG: {target_uuid} ---\n")
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                    {"tid": entidad_id}
                )

                query = select(Cfdi).where(Cfdi.uuid == target_uuid)
                result = await session.execute(query)
                comp = result.scalars().first()

                if comp:
                    f_out.write(f"Found Comprobante: {comp.folio}, Ruta: {comp.ruta_resguardo}\n")
                    if comp.ruta_resguardo:
                        all_xmls = glob.glob(os.path.join(comp.ruta_resguardo, "*.xml"))
                        files = [f for f in all_xmls if target_uuid.lower() in os.path.basename(f).lower()]
                        if files:
                            xml_path = files[0]
                            f_out.write(f"Found XML File: {xml_path}\n")
                            processor = CfdiProcessor(session)
                            res_cfdi = await processor.procesar_cfdi(
                                ruta_archivo=xml_path,
                                entidad_id=uuid.UUID(entidad_id),
                                mover_a_boveda=False
                            )
                            f_out.write(f"✅ Processed successfully! New Total: {res_cfdi.total}\n")
                        else:
                            f_out.write("❌ XML NOT Found in list.\n")
                else:
                    f_out.write("❌ Comprobante with UUID not found.\n")

                await session.commit()
        except Exception as e:
            f_out.write(f"❌ EXCEPTION: {str(e)}\n")
    print("✅ Completed safe log.")

if __name__ == "__main__":
    asyncio.run(main())
