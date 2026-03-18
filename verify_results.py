
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "prueba01")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "gestor_cfdi")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def verify():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        print("🔍 Verificando resultados en la tabla cfdis...")
        res = await conn.execute(text("SELECT uuid, tipo_comprobante, parent_uuid FROM cfdis ORDER BY issue_date"))
        rows = res.fetchall()
        for row in rows:
            print(f"UUID: {row[0]} | Tipo: {row[1]} | Parent: {row[2]}")
            
        if len(rows) >= 2:
            # Check if REP has the parent_uuid of the Invoice
            rep = next((r for r in rows if r[1] == 'P'), None)
            inv = next((r for r in rows if r[1] == 'I'), None)
            if rep and inv and rep[2] == inv[0]:
                print("\n✅ EXITO: La relación REP-Factura es DETERMINISTA y persistente.")
            else:
                print("\n❌ FALLO: La relación no se estableció correctamente.")
        else:
            print("\n⚠️ No hay suficientes registros para verificar.")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify())
