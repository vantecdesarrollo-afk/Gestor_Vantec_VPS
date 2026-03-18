import asyncio
import logging
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

# Disable SQLAlchemy LOGGING to fit buffer
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

async def main():
    async with AsyncSessionLocal() as db:
        query = select(Comprobante).where(Comprobante.folio.in_(['303', '800']))
        result = await db.execute(query)
        comps = result.scalars().all()
        
        print("\n--- INVENTARIO DE RUTAS ---")
        for c in comps:
            print(f"Folio: {c.folio}")
            print(f"UUID:  {c.uuid}")
            print(f"Ruta:  {c.ruta_resguardo}")
            print(f"Tipo:  {c.tipo_comprobante}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
