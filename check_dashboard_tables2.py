import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, func
from src.database.models_dashboard_opt import DashCfdiDocument, DashCfdiConcept

async def check():
    async with AsyncSessionLocal() as db:
        # Get all concepts with their tenant_id
        q = select(DashCfdiDocument.tenant_id, DashCfdiConcept.descripcion).join(DashCfdiConcept)
        res = await db.execute(q)
        rows = res.all()
        
        if not rows:
            print("No data found joining documents and concepts!")
        else:
            print(f"Found {len(rows)} connections:")
            for row in rows:
                print(f"Tenant: {row[0]}, Concept: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
