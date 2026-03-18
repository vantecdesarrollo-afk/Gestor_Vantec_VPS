import asyncio
import os
import shutil
from sqlalchemy import select
from src.database.session import get_db
from src.database.models import Cfdi

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def sync():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    cfdis = (await db.execute(select(Cfdi))).scalars().all()
    
    invalid_dir = r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Invalid"
    
    for c in cfdis:
        target_path = c.xml_file_path
        if not os.path.exists(target_path):
             # check if in upload or invalid for this uuid
             basename = f"{c.uuid}.xml"
             cand1 = os.path.join(invalid_dir, basename)
             cand2 = os.path.join(invalid_dir, f"{c.uuid}_error.log") # just to trace
             # wait, it might be in Invalid with Name original name!
             # like 303.xml!
             # Let's read file_name lookup?
             # No, we can just look up standard files inside Invalid that WERE 303.xml!
             # In Invalid/, files are named 303.xml, 305.xml, etc.
             # NOT UUID.xml!
             pass

import xml.etree.ElementTree as ET

async def sync():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    cfdis = (await db.execute(select(Cfdi))).scalars().all()
    
    invalid_dir = r"c:\Test_Antigravity\Gestor_CFDI_Vantec\Operacion_CFDI\Invalid"
    moved_count = 0

    if not os.path.exists(invalid_dir):
        print("Invalid directory does not exist.")
        return

    for f in os.listdir(invalid_dir):
        if not f.endswith(".xml"): continue
        p = os.path.join(invalid_dir, f)
        try:
             tree = ET.parse(p)
             root = tree.getroot()
             tfd = None
             # Find TimbreFiscalDigital
             for elem in root.iter():
                  if "TimbreFiscalDigital" in elem.tag:
                       tfd = elem
                       break
             if tfd is not None:
                  uuid_val = tfd.get("UUID")
                  if uuid_val:
                       # Match against DB Cfdi
                       match = next((c for c in cfdis if c.uuid.lower() == uuid_val.lower()), None)
                       if match:
                            target = match.xml_file_path
                            print(f"Moving {f} (UUID: {uuid_val}) -> {target}")
                            os.makedirs(os.path.dirname(target), exist_ok=True)
                            shutil.move(p, target)
                            moved_count += 1
        except Exception as e:
             print(f"Error Syncing {f}: {e}")
             
    print(f"Synced {moved_count} files back to Bóveda.")

asyncio.run(sync())
