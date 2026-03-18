import asyncio
import uuid
from sqlalchemy import text, select
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def verify_comprobantes_json():
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    entidad_id = uuid.UUID(entidad_id_str)
    
    print("Testing /api/v1/comprobantes/ serialization output...")
    output = []
    
    async with AsyncSessionLocal() as session:
        # Prender RLS
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id_str}
        )
        
        from src.api.endpoints.cfdis import router
        # Simular llamada al endpoint o correr query manual emulando el serializador
        from sqlalchemy.orm import selectinload
        query = select(Comprobante).options(selectinload(Comprobante.relaciones)).where(Comprobante.entidad_id == entidad_id)
        result = await session.execute(query)
        data = result.scalars().all()
        
        print(f"Comprobantes found: {len(data)}")
        for doc in data:
            # Emulando bloque de cfdis.py
            has_reps = hasattr(doc, 'relaciones') and doc.relaciones
            reps = []
            if has_reps:
                 reps = [
                     {"uuid_relacionado": r.uuid_relacionado, "monto_pagado": float(r.monto_pagado or 0)} 
                     for r in doc.relaciones if r.tipo_relacion == 'PAGO'
                 ]
                 
            row = {
                "folio": doc.folio,
                "uuid": doc.uuid,
                "pdf_file_path": doc.ruta_resguardo if doc.ruta_resguardo else None,
                "reps_asociados": reps
            }
            print(f"Folio {doc.folio}: pdf={row['pdf_file_path']}, reps_count={len(reps)}")
            if reps:
                print(f"  Reps: {reps}")

if __name__ == "__main__":
    asyncio.run(verify_comprobantes_json())
