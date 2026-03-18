
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Hardcoded from .env for direct access (as seen in patch_schema_direct.py)
DATABASE_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"

async def patch_deep_parsing():
    engine = create_async_engine(DATABASE_URL)
    print("🚀 VANTEC DEEP PARSING PATCH: Iniciando actualización de columnas...")
    
    commands = [
        # Añadir metadata_xml (JSONB)
        "ALTER TABLE cfdis ADD COLUMN IF NOT EXISTS metadata_xml JSONB;",
        # Añadir metodo_pago y forma_pago
        "ALTER TABLE cfdis ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(5);",
        "ALTER TABLE cfdis ADD COLUMN IF NOT EXISTS forma_pago VARCHAR(5);"
    ]

    async with engine.begin() as conn:
        for cmd in commands:
            try:
                print(f" -> Ejecutando: {cmd}")
                await conn.execute(text(cmd))
                print("    ✅ Éxito.")
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")

    await engine.dispose()
    print("\n✅ VANTEC DEEP PARSING PATCH: Proceso finalizado.")

if __name__ == "__main__":
    asyncio.run(patch_deep_parsing())
