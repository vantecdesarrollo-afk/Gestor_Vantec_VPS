import asyncio
import glob
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        print("Buscando UUID de Folio 303...")
        result = await db.execute(select(Comprobante).where(Comprobante.folio == '303'))
        cfdi = result.scalar_one_or_none()
        
        if not cfdi:
            print("Documento 303 no encontrado en la base de datos.")
            return

        uuid_str = str(cfdi.uuid)
        print(f"Folio 303 Encontrado: UUID = {uuid_str}")
        print(f"Ruta Resguardo DB: {cfdi.ruta_resguardo}")
        
        print("\n--- Buscando en Workspace por UUID ---")
        ws_paths = [
            f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\storage\\**\\*{uuid_str}*.pdf",
            f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Operacion_CFDI\\**\\*{uuid_str}*.pdf"
        ]
        
        found = False
        for p in ws_paths:
            matches = glob.glob(p, recursive=True)
            if matches:
                 print(f"✅ ¡ENCONTRADO EN WORKSPACE!: {matches[0]}")
                 found = True
                 break

        if not found:
            print("❌ No se encontró ningún archivo PDF con el UUID en el Workspace.")
            # Check for any PDF in upload folder or similar leftovers
            uploads = glob.glob(f"C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\Upload\\**\\*.pdf", recursive=True)
            print(f"\nArchivos PDF huérfanos en Upload ({len(uploads)} encontrados):")
            for u in uploads:
                print(f" - {u}")

if __name__ == "__main__":
    asyncio.run(main())
