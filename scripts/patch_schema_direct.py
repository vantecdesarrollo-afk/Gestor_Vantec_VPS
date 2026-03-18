import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Hardcoded from .env for direct access
DATABASE_URL = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"

async def patch_database():
    engine = create_async_engine(DATABASE_URL)
    print("🚀 VANTEC SCHEMA PATCH: Iniciando sincronización de columnas (Direct Mode)...")
    
    commands = [
        # 1. Estandarización de IDs y Nombres en Usuarios
        "ALTER TABLE usuarios RENAME COLUMN usuario_id TO id;",
        "ALTER TABLE usuarios RENAME COLUMN password_hash TO hashed_password;",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_superadmin BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) DEFAULT 'LOCAL';",
        
        # 2. Estandarización de IDs y Nombres en Entidades
        "ALTER TABLE entidades_fiscales RENAME COLUMN entidad_id TO id;",
        "ALTER TABLE entidades_fiscales ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);",
        
        # 3. Migración de Cfdi
        "ALTER TABLE cfdis RENAME COLUMN tenant_id TO entidad_id;",
        
        # 4. Limpieza de tablas relacionadas
        "ALTER TABLE cfdi_relacionados DROP COLUMN IF EXISTS tenant_id;"
    ]

    async with engine.begin() as conn:
        for cmd in commands:
            try:
                print(f" -> Ejecutando: {cmd}")
                await conn.execute(text(cmd))
                print("    ✅ Éxito.")
            except Exception as e:
                if "no existe" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"    ⚠️ Omitido: {str(e).splitlines()[0]}")
                else:
                    print(f"    ❌ Error: {str(e)}")

    await engine.dispose()
    print("\n✅ VANTEC SCHEMA PATCH: Sincronización finalizada.")

if __name__ == "__main__":
    asyncio.run(patch_database())
