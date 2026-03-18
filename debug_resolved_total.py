import asyncio
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante
from sqlalchemy.orm import selectinload

async def main():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    target_uuid = "af41872d-1e12-44ec-9d58-614b23e9655c"
    
    with open("resolved_total_debug.txt", "w", encoding="utf-8") as f:
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT set_config('app.current_tenant_id', :tid, true)"), {"tid": entidad_id})
                
                query = (
                    select(Comprobante)
                    .options(selectinload(Comprobante.relaciones))
                    .where(Comprobante.uuid == target_uuid)
                )
                result = await session.execute(query)
                comp = result.scalars().first()

                if comp:
                    f.write("--- CALCULATION DEBUG ---\n")
                    f.write(f"comp.uuid: {comp.uuid}\n")
                    f.write(f"comp.tipo_comprobante: {comp.tipo_comprobante}\n")
                    f.write(f"comp.total: {comp.total}\n")
                    f.write(f"comp.relaciones count: {len(comp.relaciones)}\n")

                    # 1. reps_list building exactly like line 159
                    reps_list = [
                        {
                            "uuid": str(r.uuid_padre if str(r.uuid_relacionado).lower() == str(comp.uuid).lower() else r.uuid_relacionado),
                            "monto": float(r.monto_pagado or 0),
                            "tipo": r.tipo_relacion
                        } for r in comp.relaciones if r.tipo_relacion == 'PAGO'
                    ]
                    f.write(f"reps_list len: {len(reps_list)}\n")
                    if reps_list:
                         f.write(f"First item: {reps_list[0]}\n")

                    total_monto_pago = sum(float(r["monto"]) for r in reps_list)
                    f.write(f"total_monto_pago: {total_monto_pago}\n")

                    p_cond = comp.tipo_comprobante and comp.tipo_comprobante.strip().upper() == 'P'
                    f.write(f"Condition comp.tipo_comprobante == 'P': {p_cond}\n")
                    
                    p_gt = total_monto_pago > 0
                    f.write(f"total_monto_pago > 0: {p_gt}\n")

                    resolved_total = total_monto_pago if p_cond and p_gt else float(comp.total or 0)
                    f.write(f"resolved_total: {resolved_total}\n")
                else:
                    f.write("❌ Comprobante no encontrado.\n")
        except Exception as e:
            f.write(f"❌ EXCEPTION: {str(e)}\n")
    print("✅ Debug complete.")

if __name__ == "__main__":
    asyncio.run(main())
