import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"

async def final_patch():
    engine = create_async_engine(DATABASE_URL)
    print("🚀 VANTEC FINAL PATCH: Aplicando correcciones de última milla...")
    
    commands = [
        # Renombrar columna de contraseña si existe
        "ALTER TABLE usuarios RENAME COLUMN password_hash TO hashed_password;",
        # Añadir columnas faltantes si no existen
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_superadmin BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;",
        "ALTER TABLE entidades_fiscales ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);",
    ]

    async with engine.begin() as conn:
        for cmd in commands:
            try:
                print(f" -> {cmd}")
                await conn.execute(text(cmd))
                print("    ✅ Éxito.")
            except Exception as e:
                print(f"    ⚠️ INFO: {str(e).splitlines()[0]}")

    await engine.dispose()
    print("\n✅ SCHEMA SYNC COMPLETO.")

if __name__ == "__main__":
    asyncio.run(final_patch())
