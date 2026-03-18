import asyncio
import uuid
from sqlalchemy import select, update, func
from src.database.session import AsyncSessionLocal, engine
from src.database.models import Base, EntidadFiscal, Cfdi

async def link_orphans():
    log = ["[Vantec Data Rescue] Iniciando vinculación de datos..."]
    
    OLD_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    TARGET_RFC = "VCO1307234VA"
    
    try:
        async with AsyncSessionLocal() as db:
            # 1. Buscar la Entidad Fiscal objetivo
            result = await db.execute(select(EntidadFiscal).where(EntidadFiscal.rfc == TARGET_RFC))
            target_entidad = result.scalar_one_or_none()
            
            if not target_entidad:
                log.append(f" -> ERROR: No se encontró la entidad con RFC {TARGET_RFC}")
                return

            target_id = target_entidad.id
            log.append(f" -> Entidad Real encontrada: {target_entidad.razon_social} (ID: {target_id})")

            # 2. Buscar registros desvinculados o en la entidad vieja
            res = await db.execute(select(func.count(Cfdi.cfdi_id)).where((Cfdi.entidad_id == None) | (Cfdi.entidad_id == OLD_ID)))
            count = res.scalar()
            
            if count > 0:
                log.append(f" -> Detectados {count} registros para re-vincular.")
                
                # 3. Vincular masivamente
                update_stmt = update(Cfdi).where((Cfdi.entidad_id == None) | (Cfdi.entidad_id == OLD_ID)).values(entidad_id=target_id)
                await db.execute(update_stmt)
                await db.commit()
                log.append(f" Success: {count} registros movidos a {TARGET_RFC}")
            else:
                log.append(" Success: No se detectaron registros para vincular.")
    except Exception as ex:
        log.append(f"CRITICAL ERROR: {ex}")
        import traceback
        log.append(traceback.format_exc())
    finally:
        with open("rescue_log.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(log))

if __name__ == "__main__":
    asyncio.run(link_orphans())
