import asyncio
import uuid
from sqlalchemy import select, func, or_
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, CfdiRelacionado

async def verify_ppd():
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    entidad_id = uuid.UUID(entidad_id_str)

    async with AsyncSessionLocal() as session:
        # Prender RLS
        await session.execute(
            select(func.set_config('app.current_tenant_id', entidad_id_str, True))
        )

        query = select(Comprobante).where(Comprobante.entidad_id == entidad_id)
        result = await session.execute(query)
        data = result.scalars().all()

        ppd_data = [c for c in data if c.metodo_pago == 'PPD']
        print(f"PPD Comprobantes found: {len(ppd_data)}")
        for c in ppd_data:
            print(f"  - Folio {c.folio}: UUID={c.uuid}")

        relations_res = await session.execute(
            select(CfdiRelacionado).where(
                CfdiRelacionado.tipo_relacion == 'PAGO',
                or_(
                    func.lower(CfdiRelacionado.uuid_padre).in_([str(c.uuid).lower() for c in ppd_data]),
                    func.lower(CfdiRelacionado.uuid_relacionado).in_([str(c.uuid).lower() for c in ppd_data])
                )
            )
        )
        relations = relations_res.scalars().all()
        print(f"Relations found for PPDs: {len(relations)}")
        for r in relations:
            print(f"  - Relation: Padre={r.uuid_padre}, Rel={r.uuid_relacionado}")

        linked_uuids = {r.uuid_padre.lower() for r in relations}.union({r.uuid_relacionado.lower() for r in relations})
        orphans = [c for c in ppd_data if str(c.uuid).lower() not in linked_uuids]

        import json
        output_data = {
            "ppds": [{"folio": c.folio, "uuid": str(c.uuid)} for c in ppd_data],
            "relations": [{"padre": r.uuid_padre, "relacionado": r.uuid_relacionado} for r in relations],
            "linked_uuids": list(linked_uuids),
            "orphans": [{"folio": c.folio, "uuid": str(c.uuid)} for c in orphans]
        }
        with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\verify_ppd_output.json", "w") as f:
            json.dump(output_data, f, indent=4)
        print("JSON SAVED")

if __name__ == "__main__":
    asyncio.run(verify_ppd())
