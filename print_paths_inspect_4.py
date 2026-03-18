import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def main():
    async with AsyncSessionLocal() as db:
        query = select(Comprobante).where(Comprobante.folio.in_(['303', '800']))
        result = await db.execute(query)
        comps = result.scalars().all()
        
        with open("ruta_output.txt", "w", encoding="utf-8") as f:
            f.write("\n--- INVENTARIO DE RUTAS ---\n")
            for c in comps:
                f.write(f"Folio: {c.folio}\n")
                f.write(f"UUID:  {c.uuid}\n")
                f.write(f"Ruta:  {c.ruta_resguardo}\n")
                f.write(f"Tipo:  {c.tipo_comprobante}\n")
                f.write("-" * 20 + "\n")
        print("✅ Output written to ruta_output.txt")

if __name__ == "__main__":
    asyncio.run(main())
