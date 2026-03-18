import asyncio
import uuid
from sqlalchemy import text, select, or_, func
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, CfdiRelacionado
from src.api.endpoints.analytics import get_dashboard_analytics

async def debug_analytics():
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    entidad_id = uuid.UUID(entidad_id_str)
    
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    async with AsyncSessionLocal() as session:
        log("Injecting RLS context...")
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id_str}
        )
        
        try:
            # 1. Query Comprobantes
            query = select(Comprobante).where(Comprobante.entidad_id == entidad_id)
            result = await session.execute(query)
            data = result.scalars().all()
            log(f"Comprobantes found: {len(data)}")
            
            ppd_data = [c for c in data if c.metodo_pago == 'PPD']
            log(f"PPD documents: {[c.folio for c in ppd_data]}")
            for c in ppd_data:
                log(f"  PPD Folio: {c.folio}, UUID: {c.uuid}")
                
            # 2. Query Relations with current context
            # We want to see if relation 519 is visible here!
            relations_res = await session.execute(select(CfdiRelacionado))
            all_rels = relations_res.scalars().all()
            log(f"Total cfdi_relacionados visible under RLS: {len(all_rels)}")
            for r in all_rels:
                log(f"  Visible Relation: ID={r.id}, Padre={r.uuid_padre}, Relacionado={r.uuid_relacionado}, cfdi_id={r.cfdi_id}")
                
            # 3. Simulate analytics logic
            relations_res2 = await session.execute(
                select(CfdiRelacionado).where(
                    CfdiRelacionado.tipo_relacion == 'PAGO',
                    or_(
                        func.lower(CfdiRelacionado.uuid_padre).in_([str(c.uuid).lower() for c in ppd_data]),
                        func.lower(CfdiRelacionado.uuid_relacionado).in_([str(c.uuid).lower() for c in ppd_data])
                    )
                )
            )
            relations = relations_res2.scalars().all()
            log(f"Matched relations for analytics: {len(relations)}")
            for r in relations:
                 log(f"  Matched: {r.id}")
            
            linked_uuids = {r.uuid_padre.lower() for r in relations}.union({r.uuid_relacionado.lower() for r in relations})
            log(f"Linked UUIDs (lower): {linked_uuids}")
            
            p_docs = [c for c in ppd_data if str(c.uuid).lower() not in linked_uuids]
            log(f"PPD Pendientes count calculated: {len(p_docs)}")
            for c in p_docs:
                log(f"  Pending: {c.folio}")
                
        except Exception as e:
            log(f"Error: {e}")
            
    with open("debug_analytics_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(debug_analytics())
