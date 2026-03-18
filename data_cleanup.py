import asyncio
import uuid
import sys
import os
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import EntidadFiscal, Cfdi

async def purge_malformed_links():
    print("🚀 Vantec Data Integrity Engine - Starting Purge")
    try:
        async with AsyncSessionLocal() as db:
            # 1. Fetch Entidades map
            print("[*] Fetching entities...")
            entidades_result = await db.execute(select(EntidadFiscal))
            entidades_map = {e.id: e.rfc for e in entidades_result.scalars().all()}
            print(f"[+] Loaded {len(entidades_map)} entities.")

            # 2. Fetch all linked CFDIs
            print("[*] Querying linked CFDIs...")
            result = await db.execute(
                select(Cfdi).where(Cfdi.entidad_id.isnot(None))
            )
            cfdis = result.scalars().all()
            print(f"[*] Analyzing {len(cfdis)} records...")

            purged_count = 0
            for cfdi in cfdis:
                entidad_rfc = entidades_map.get(cfdi.entidad_id)
                if not entidad_rfc or entidad_rfc not in [cfdi.rfc_emisor, cfdi.rfc_receptor]:
                    # CTO REGLA DE ORO: Si no es emisor ni receptor, el registro es inválido.
                    # Como entidad_id es non-nullable, procedemos con el BORRADO DIRECTO.
                    await db.delete(cfdi)
                    purged_count += 1
            
            if purged_count > 0:
                await db.commit()
                print(f"✅ EXITO: Se han ELIMINADO {purged_count} registros de CFDI por inconsistencia de RFC.")
            else:
                print("✨ Limpieza completa: No se detectaron vínculos corruptos.")
                
    except Exception as e:
        print(f"❌ ERROR CRITICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(purge_malformed_links())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
