import asyncio
from sqlalchemy import select, text
from src.database.session import engine, AsyncSessionLocal
from src.database.models import Comprobante, Tenant

async def test_db():
    async with AsyncSessionLocal() as session:
        # Check all tenants
        print("--- VERIFICACIÓN DE INQUILINOS (TENANTS) ---")
        t_result = await session.execute(select(Tenant.tenant_id, Tenant.rfc, Tenant.business_name))
        for row in t_result.all():
            print(f"[{row[0]}] RFC: {row[1]} -> {row[2]}")
        
        # Test specific Tenant Planeta
        t_planeta_res = await session.execute(select(Tenant).where(Tenant.rfc == 'EPM880422LV3'))
        t_planeta = t_planeta_res.scalar_one_or_none()
        
        if t_planeta:
            print("\n--- EJECUCIÓN AISLADA (PLANETA) ---")
            query = select(Comprobante.uuid, Comprobante.folio, Comprobante.rfc_receptor, Comprobante.entidad_id).where(Comprobante.entidad_id == t_planeta.tenant_id).limit(5)
            c_result = await session.execute(query)
            items = c_result.all()
            if not items:
                 print("Planeta no tiene documentos o la DB filtró correctamente los ajenos.")
            for row in items:
                 print(f"Documento Planeta -> UUID: {row[0][:8]}... Folio: {row[1]} Receptor: {row[2]}")
                 
        # Test Vantec    
        t_vantec_res = await session.execute(select(Tenant).where(Tenant.rfc == 'CMES8901177E8')) 
        t_vantec = t_vantec_res.scalar_one_or_none()
        if t_vantec:
            print("\n--- EJECUCIÓN AISLADA (VANTEC) ---")
            query = select(Comprobante.uuid, Comprobante.folio, Comprobante.rfc_receptor, Comprobante.entidad_id).where(Comprobante.entidad_id == t_vantec.tenant_id).limit(5)
            c_result = await session.execute(query)
            for row in c_result.all():
                 print(f"Documento Vantec -> UUID: {row[0][:8]}... Folio: {row[1]} Receptor: {row[2]}")

if __name__ == "__main__":
    asyncio.run(test_db())
