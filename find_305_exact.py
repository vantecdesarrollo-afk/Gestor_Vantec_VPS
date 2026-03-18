import asyncio
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def main():
    # USAR EL MISMO ENTIDAD ID
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id}
        )
        
        query = select(Comprobante).where(Comprobante.folio.like('%305%'))
        result = await session.execute(query)
        comps = result.scalars().all()
        
        print("\n--- INVENTARIO FOLIO %305% ---")
        for c in comps:
             print(f"Folio (DB): '{c.folio}'")
             print(f"UUID:       '{c.uuid}'")
             print(f"Ruta:       '{c.ruta_resguardo}'")
             print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
