import asyncio
from sqlalchemy import select, or_, cast, String, func
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, CfdiRelacionado

async def test_or_join():
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    async with AsyncSessionLocal() as session:
        try:
            # Query Comprobante 804 (Invoice)
            query = select(Comprobante).where(Comprobante.folio == '0000000804')
            result = await session.execute(query)
            comp = result.scalar_one_or_none()
            
            if comp:
                log(f"Found Comprobante: {comp.folio}, UUID: {comp.uuid}")
                
                # Simulate OR relationship query
                # Condition: relation matches comp.uuid in either padre OR relacionado
                rel_query = select(CfdiRelacionado).where(
                    or_(
                        func.lower(CfdiRelacionado.uuid_padre) == str(comp.uuid).lower(),
                        func.lower(CfdiRelacionado.uuid_relacionado) == str(comp.uuid).lower()
                    )
                )
                rel_result = await session.execute(rel_query)
                relations = rel_result.scalars().all()
                
                log(f"Relations found with OR query: {len(relations)}")
                for r in relations:
                    log(f"  ID: {r.id}, Padre: {r.uuid_padre}, Relacionado: {r.uuid_relacionado}, Tipo: {r.tipo_relacion}")
            else:
                log("Comprobante 804 not found.")
                
        except Exception as e:
            log(f"Error: {e}")
            
    with open("verify_or_join_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(test_or_join())
