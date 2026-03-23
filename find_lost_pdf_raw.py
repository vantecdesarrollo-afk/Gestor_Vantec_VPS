import asyncio
import glob
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        print("Buscando UUID de Folio 303...")
        # RAW SQL string query to avoid ORM lazy loads
        result = await db.execute(text("SELECT uuid, ruta_resguardo FROM comprobantes WHERE folio = '303'"))
        row = result.fetchone()
        
        if not row:
            print("Documento 303 no encontrado en la base de datos.")
            return

        uuid_str = str(row[0]).upper()
        ruta_resguardo = row[1] or ""
        print(f"Folio 303 Encontrado: UUID = {uuid_str}")
        print(f"Ruta Resguardo DB: {ruta_resguardo}")
        
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
                
            # Check other Candidates to assist diagnostics
            if uuid_str:
                cfdi_dir = r"C:\ITC\Fappeal\Planeta\Outfile\SAT\Factura"
                cfdi_matches = glob.glob(f"{cfdi_dir}\\**\\*{uuid_str}*.pdf", recursive=True)
                if cfdi_matches:
                    print(f"✅ ¡ENCONTRADO EN OUTFILE!: {cfdi_matches[0]}")

if __name__ == "__main__":
    asyncio.run(main())
