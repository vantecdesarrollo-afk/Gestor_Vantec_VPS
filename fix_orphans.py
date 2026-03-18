import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal, Cfdi
from sqlalchemy import select, update

async def fix_orphans():
    print("🚀 Iniciando vinculación de datos huérfanos...")
    async with AsyncSessionLocal() as db:
        # 1. Buscar ID de Vantec
        q = select(EntidadFiscal.id).where(EntidadFiscal.rfc == 'VCO1307234VA')
        result = await db.execute(q)
        vantec_id = result.scalar()
        
        if not vantec_id:
            print("❌ ERROR: No se encontró la entidad con RFC VCO1307234VA")
            return

        print(f"✅ Entidad Vantec encontrada (ID: {vantec_id})")
        
        # 2. Actualizar CFDIs NULL
        upd = (
            update(Cfdi)
            .where(Cfdi.entidad_id == None)
            .values(entidad_id=vantec_id)
        )
        res = await db.execute(upd)
        await db.commit()
        
        print(f"📊 Vinculación completada. Registros afectados: {res.rowcount}")

if __name__ == "__main__":
    asyncio.run(fix_orphans())
