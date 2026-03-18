import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import CfdiRelacionado, Comprobante

async def verify_all_relaciones():
    output = []
    def log(msg):
        output.append(str(msg))
        
    async with AsyncSessionLocal() as session:
        try:
            log("Querying all CfdiRelacionado records...")
            query = select(CfdiRelacionado)
            result = await session.execute(query)
            relaciones = result.scalars().all()
            
            log(f"Total CfdiRelacionado records: {len(relaciones)}")
            
            # Print first 5 for format check
            for r in relaciones[:5]:
                log(f"  ID: {r.id}, Padre: {r.uuid_padre}, Relacionado: {r.uuid_relacionado}, Tipo: {r.tipo_relacion}")
                
            log("\nComparing with Comprobante UUIDs...")
            query_comp = select(Comprobante)
            result_comp = await session.execute(query_comp)
            comprobantes = result_comp.scalars().all()
            
            comp_uuids = [str(c.uuid).lower() for c in comprobantes]
            log(f"Comprobante UUIDs in DB (lowercase): {comp_uuids}")
            
            matches = 0
            for r in relaciones:
                p_uuid = r.uuid_padre.lower() if r.uuid_padre else ""
                if p_uuid in comp_uuids:
                    matches += 1
                    log(f"  MATCH: Relation {r.id} parent {r.uuid_padre} matches Comprobante!")
                    
            log(f"\nTotal matches found: {matches}")
            
        except Exception as e:
            log(f"Error: {e}")
            
    with open("verify_all_relaciones_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(verify_all_relaciones())
