import asyncio
from src.services.parser.cfdi_parser import process_inbound_file
from src.database.session import get_db
import os

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def test_run():
    # Find a sample file in Invalid or Upload
    test_file = r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Upload\303.xml"
    if not os.path.exists(test_file):
        print("Upload/303.xml not found for testing execution.")
        return

    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    
    intent_tenant = "00000000-0000-0000-0000-000000000000" # Dummy or we look up one
    from sqlalchemy import select
    from src.database.models import Tenant
    res = await db.execute(select(Tenant))
    tenant = res.scalars().first()
    if tenant:
         intent_tenant = tenant.tenant_id
         
    print(f"Testing ingestion with tenant: {intent_tenant}")
    try:
         # Copy to procesamiento first like watcher does
         proc_path = r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Processing\303.xml"
         import shutil
         os.makedirs(os.path.dirname(proc_path), exist_ok=True)
         shutil.copy(test_file, proc_path)
         
         await process_inbound_file(
              xml_path=proc_path,
              failed_dir=r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Invalid",
              log_dir=r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\logs",
              db=db,
              entidad_id=intent_tenant
         )
         print("Test Ingestion Completed without crashes.")
    except Exception as e:
         print(f"Test Crashed: {e}")

if __name__ == "__main__":
    asyncio.run(test_run())
