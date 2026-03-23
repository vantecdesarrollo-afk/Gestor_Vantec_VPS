import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, func
from src.database.models_dashboard_opt import DashCfdiDocument, DashCfdiConcept

async def check():
    async with AsyncSessionLocal() as db:
        docs_count = (await db.execute(select(func.count()).select_from(DashCfdiDocument))).scalar()
        concepts_count = (await db.execute(select(func.count()).select_from(DashCfdiConcept))).scalar()
        
        print(f"Total dash_cfdi_documents: {docs_count}")
        print(f"Total dash_cfdi_concepts: {concepts_count}")

if __name__ == "__main__":
    asyncio.run(check())
