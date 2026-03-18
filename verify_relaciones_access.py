import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante, CfdiRelacionado

async def verify_relations():
    async with AsyncSessionLocal() as session:
        try:
            print("Querying Comprobante with relations...")
            query = select(Comprobante).options(selectinload(Comprobante.relaciones))
            result = await session.execute(query)
            comprobantes = result.scalars().all()
            
            print(f"Total Comprobantes: {len(comprobantes)}")
            
            for c in comprobantes:
                print(f"\nComprobante UUID: {c.uuid}, Folio: {c.folio}")
                try:
                    relations = c.relaciones
                    print(f"  Relations count: {len(relations)}")
                    for r in relations:
                        print(f"    - Relacionado: {r.uuid_relacionado}, Tipo: {r.tipo_relacion}")
                except Exception as e:
                    print(f"  Error accessing relaciones: {e}")
                    
        except Exception as e:
            print(f"Error executing query: {e}")

if __name__ == "__main__":
    asyncio.run(verify_relations())
