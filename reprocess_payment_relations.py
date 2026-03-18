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
    with open("reprocess_log.txt", "w", encoding="utf-8") as f:
        f.write("--- REPROCESANDO RELACIONES ---\n")
        try:
            async with AsyncSessionLocal() as session:
                # Set tenant for RLS
                await session.execute(
                    text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                    {"tid": entidad_id}
                )

                # 1. Get all payments
                query = select(Comprobante).where(Comprobante.tipo_comprobante == 'P')
                result = await session.execute(query)
                payments = result.scalars().all()

                f.write(f"Found {len(payments)} payment documents.\n")
                processor = CfdiProcessor(session)

                fixed_count = 0
                for p in payments:
                    if p.ruta_resguardo:
                        files = glob.glob(os.path.join(p.ruta_resguardo, f"*{p.uuid}*.xml"))
                        if files:
                            xml_path = files[0]
                            # procesar_cfdi handles upsert and relations
                            res_cfdi = await processor.procesar_cfdi(
                                ruta_archivo=xml_path,
                                entidad_id=uuid.UUID(entidad_id),
                                mover_a_boveda=False
                            )
                            f.write(f"✅ Processed Folio {p.folio} (UUID: {p.uuid}): set sub_relations, total: {res_cfdi.total}\n")
                            fixed_count += 1
                        else:
                            f.write(f"❌ XML NOT Found for Folio {p.folio} (UUID: {p.uuid}) in {p.ruta_resguardo}\n")

                await session.commit()
                f.write(f"\nSuccessfully reprocessed {fixed_count} payments.\n")
        except Exception as e:
            f.write(f"\n❌ EXCEPTION: {str(e)}\n")
    
    print("✅ Complete.")

if __name__ == "__main__":
    asyncio.run(main())
