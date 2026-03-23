import asyncio
import glob
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        print("Buscando Documento por Total 28820.03...")
        # Query by Total amount instead of exact string folio
        result = await db.execute(text("SELECT uuid, folio, ruta_resguardo FROM comprobantes WHERE total = 28820.03 OR total = 28820"))
        rows = result.fetchall()
        
        if not rows:
            print("Documento no encontrado por Total.")
            return

        for row in rows:
            uuid_str = str(row[0]).upper()
            folio_db = row[1]
            ruta_resguardo = row[2] or ""
            print(f"--- Encontrado ---")
            print(f"Folio en DB: '{folio_db}'")
            print(f"UUID: {uuid_str}")
            print(f"Ruta Resguardo DB: {ruta_resguardo}")
            
            print("Buscando en Workspace...")
            ws_paths = [
                f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage\\**\\*{uuid_str}*.pdf",
                f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Operacion_CFDI\\**\\*{uuid_str}*.pdf"
            ]
            for p in ws_paths:
                matches = glob.glob(p, recursive=True)
                if matches:
                     print(f"  ✅ ¡ENCONTRADO EN WORKSPACE!: {matches[0]}")
            
            print("Buscando por Folio Directo en Upload...")
            clean_folio = str(folio_db).lstrip('0') if folio_db else ""
            uploads = glob.glob(f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Upload\\**\\*{clean_folio}*.pdf", recursive=True)
            for u in uploads:
                print(f"  ✅ ¡ENCONTRADO EN UPLOAD!: {u}")

if __name__ == "__main__":
    asyncio.run(main())
