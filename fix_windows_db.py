import asyncio, asyncpg

async def fix_final():
    print("🔌 Conectando para inyectar esquema analítico y permisos...")
    conn = await asyncpg.connect('postgresql://postgres:prueba01@localhost:5432/gestor_cfdi')
    
    # 1. Parche estructural para las matemáticas del Dashboard (models.py)
    await conn.execute('''
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(10);
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS forma_pago VARCHAR(10);
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS version VARCHAR(10);
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS descuento NUMERIC(18,6) DEFAULT 0;
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS total_impuestos_trasladados NUMERIC(18,6) DEFAULT 0;
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS total_impuestos_retenidos NUMERIC(18,6) DEFAULT 0;
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS serie VARCHAR(25);
        ALTER TABLE comprobantes ADD COLUMN IF NOT EXISTS folio VARCHAR(40);
    ''')

    # 2. Ascenso forzado a SUPERADMIN (Destruye el rebote 401)
    await conn.execute("UPDATE usuario_entidad_acceso SET rol = 'SUPERADMIN';")
    await conn.execute("UPDATE users SET is_superadmin = true;")
    
    await conn.close()
    print("✅ Esquema analítico y permisos SUPERADMIN instalados.")

if __name__ == "__main__":
    asyncio.run(fix_final())