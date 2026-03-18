import asyncio
import os
import uuid
from src.services.parser.cfdi_parser import process_inbound_file
from src.database.session import AsyncSessionLocal
from src.database.models import Tenant, Cfdi
from sqlalchemy import select, text

async def debug():
    async with AsyncSessionLocal() as db:
        # 2. Find first tenant
        tenant = (await db.execute(select(Tenant).limit(1))).scalar_one_or_none()
        if not tenant:
             print("No tenant in DB")
             return
        entidad_id = tenant.tenant_id
        
        proc_dir = r"C:\Vantec\DropZone\processing"
        if not os.path.exists(proc_dir):
             print(f"Dir {proc_dir} not found")
             return
             
        files = [f for f in os.listdir(proc_dir) if f.endswith(".xml")]
        print(f"Found {len(files)} XMLs to process in {proc_dir}")

        failed_dir = r"C:\Vantec\DropZone\failed"
        log_dir = r"C:\Vantec\DropZone\failed\logs"
        os.makedirs(failed_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        for f in files:
             xml_path = os.path.join(proc_dir, f)
             print(f"\nProcessing: {xml_path}")
             try:
                  await process_inbound_file(xml_path, failed_dir, log_dir, db, entidad_id)
                  print(f"-> Success: {f}")
             except Exception as e:
                  import traceback
                  print(f"-> EXCEPTION CAUGHT for {f}:")
                  traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(debug())
