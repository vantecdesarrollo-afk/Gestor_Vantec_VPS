import asyncio
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def main():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id}
        )
        query = select(Comprobante).where(Comprobante.folio.like('%305%'))
        result = await session.execute(query)
        comps = result.scalars().all()
        
        with open("find_output.txt", "w", encoding="utf-8") as f:
            f.write("\n--- INVENTARIO FOLIO %305% ---\n")
            for c in comps:
                f.write(f"Folio (DB): '{c.folio}'\n")
                f.write(f"UUID:       '{c.uuid}'\n")
                f.write(f"Ruta:       '{c.ruta_resguardo}'\n")
                f.write("-" * 20 + "\n")
        print("✅ Written to find_output.txt")

if __name__ == "__main__":
    asyncio.run(main())
