import asyncio
from sqlalchemy import select, text
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante
import os
import glob

async def main():
    entidad_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    async with AsyncSessionLocal() as session:
        # Set tenant for RLS
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id}
        )
        
        query = select(Comprobante).where(Comprobante.folio == '305')
        result = await session.execute(query)
        comp = result.scalars().first()
        
        if comp:
            print(f"--- FOLIO 305 FOUND ---")
            print(f"UUID:  {comp.uuid}")
            print(f"Ruta:  {comp.ruta_resguardo}")
            print(f"Total: {comp.total}")
            print(f"Tipo:  {comp.tipo_comprobante}")
            
            if comp.ruta_resguardo:
                files = glob.glob(os.path.join(comp.ruta_resguardo, f"*{comp.uuid}*.xml"))
                if files:
                    print(f"✅ XML Found: {files[0]}")
                else:
                    print(f"❌ XML NOT Found in {comp.ruta_resguardo}")
        else:
            print("❌ Folio 305 not found in database.")

if __name__ == "__main__":
    asyncio.run(main())
