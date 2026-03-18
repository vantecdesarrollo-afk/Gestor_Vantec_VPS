import asyncio
import uuid
import sys
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def verify_data():
    output = []
    def log(msg):
        print(msg)
        output.append(str(msg))
        
    async with AsyncSessionLocal() as session:
        try:
            query = select(Comprobante)
            result = await session.execute(query)
            comprobantes = result.scalars().all()
            
            log(f"Total Comprobantes found: {len(comprobantes)}")
            
            entidades = {}
            for c in comprobantes:
                eid = str(c.entidad_id)
                if eid not in entidades:
                    entidades[eid] = []
                entidades[eid].append(c)
                
            for eid, docs in entidades.items():
                log(f"\nEntidad ID: {eid}")
                log(f"Count: {len(docs)}")
                ingresos = sum(float(c.total or 0) for c in docs if c.tipo_comprobante == 'I')
                egresos = sum(float(c.total or 0) for c in docs if c.tipo_comprobante == 'E')
                ppd = len([c for c in docs if c.metodo_pago == 'PPD'])
                
                log(f"  Calculated Ingresos: {ingresos}")
                log(f"  Calculated Egresos: {egresos}")
                log(f"  PPD count: {ppd}")
                
                for c in docs:
                    log(f"    Folio: {c.folio}, Tipo: {c.tipo_comprobante}, Metodo: {c.metodo_pago}, Total: {c.total}")
                    
        except Exception as e:
            log(f"Error: {e}")
            
    with open("verify_dashboard_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(verify_data())
