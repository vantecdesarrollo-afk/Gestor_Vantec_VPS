import asyncio
import uuid
from sqlalchemy import select, text, func
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, Cfdi, CfdiRelacionado

async def inspect():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    output = []
    try:
        async with AsyncSessionLocal() as session:
            # Set tenant for RLS
            await session.execute(
                text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                {"tid": entidad_id}
            )
            
            target_uuid = "d2a9308b-f4d9-4357-8adf-de186a7ef5d1"
            
            output.append("--- Checking Comprobante ---")
            q_comp = select(Comprobante).where(Comprobante.uuid == uuid.UUID(target_uuid))
            res_comp = await session.execute(q_comp)
            comp = res_comp.scalars().first()
            if comp:
                output.append("Comprobante Found!")
                output.append(f"UUID: {comp.uuid}")
                output.append(f"Serie: {comp.serie}, Folio: {comp.folio}")
                output.append(f"Tipo: {comp.tipo_comprobante}")
                output.append(f"Total: {comp.total}")
                output.append(f"Ruta: {comp.ruta_resguardo}")
            else:
                output.append("Comprobante NOT Found")

            output.append("\n--- Checking Cfdi ---")
            q_cfdi = select(Cfdi).where(func.lower(Cfdi.uuid) == target_uuid.lower())
            res_cfdi = await session.execute(q_cfdi)
            cfdi = res_cfdi.scalars().first()
            if cfdi:
                output.append("Cfdi Found!")
                output.append(f"UUID: {cfdi.uuid}")
                output.append(f"Total: {cfdi.total}")
            else:
                output.append("Cfdi NOT Found")

            output.append("\n--- Checking Relaciones (Padre) ---")
            q_rel_p = select(CfdiRelacionado).where(func.lower(CfdiRelacionado.uuid_padre) == target_uuid.lower())
            res_rel_p = await session.execute(q_rel_p)
            rels_p = res_rel_p.scalars().all()
            output.append(f"Found {len(rels_p)} relaciones as Padre")
            for r in rels_p:
                output.append(f"  -> Relacionado: {r.uuid_relacionado}, Tipo: {r.tipo_relacion}, Monto: {r.monto_pagado}")

            output.append("\n--- Checking Relaciones (Relacionado) ---")
            q_rel_r = select(CfdiRelacionado).where(func.lower(CfdiRelacionado.uuid_relacionado) == target_uuid.lower())
            res_rel_r = await session.execute(q_rel_r)
            rels_r = res_rel_r.scalars().all()
            output.append(f"Found {len(rels_r)} relaciones as Relacionado")
            for r in rels_r:
                output.append(f"  <- Padre: {r.uuid_padre}, Tipo: {r.tipo_relacion}, Monto: {r.monto_pagado}")

    except Exception as e:
        output.append(f"\n❌ EXCEPTION: {str(e)}")

    with open("inspect_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(inspect())
