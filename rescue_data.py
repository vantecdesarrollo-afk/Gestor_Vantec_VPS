import asyncio
import uuid
from src.database.session import engine
from sqlalchemy import text

async def rescue():
    log = ["--- INICIANDO RESCATE DE DATOS ---"]
    REAL_ID = 'e6f64bb0-3971-4cc8-b883-cd183eca77d7'
    OLD_ID = '550e8400-e29b-41d4-a716-446655440000'
    
    try:
        async with engine.begin() as conn:
            # 1. Sincronizar Tenant
            log.append(f"1. Insertando {REAL_ID} en tabla 'tenants'...")
            # En la tabla 'tenants' la columna es 'tenant_id', no 'id'
            await conn.execute(text(f"""
                INSERT INTO tenants (tenant_id, rfc, business_name, is_active) 
                VALUES ('{REAL_ID}', 'VCO1307234VA', 'Vantec Consultores', true) 
                ON CONFLICT (tenant_id) DO NOTHING
            """))
            log.append("   -> OK")
            
            # 2. Vincular CFDIs (aquí sí es entidad_id según el error FK anterior)
            log.append(f"2. Re-vinculando CFDIs de {OLD_ID} o NULL a {REAL_ID}...")
            res = await conn.execute(text(f"""
                UPDATE cfdis 
                SET entidad_id = '{REAL_ID}' 
                WHERE entidad_id IS NULL OR entidad_id = '{OLD_ID}'
            """))
            log.append(f"   -> OK (Registros afectados: {res.rowcount})")
            
    except Exception as e:
        log.append(f"FATAL ERROR: {e}")
        import traceback
        log.append(traceback.format_exc())
    
    with open("final_rescue_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print("\n".join(log))

if __name__ == "__main__":
    asyncio.run(rescue())
