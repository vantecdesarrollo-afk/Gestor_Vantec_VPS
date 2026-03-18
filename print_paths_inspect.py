import asyncio
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.database.models import Comprobante

async def main():
    async for db in get_db():
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
        break

if __name__ == "__main__":
    asyncio.run(main())
