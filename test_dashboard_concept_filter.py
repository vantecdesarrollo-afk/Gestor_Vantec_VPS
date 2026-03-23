import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select
from src.database.models_dashboard_opt import DashCfdiDocument, DashCfdiConcept
from src.api.endpoints.auth import get_active_entidad
from fastapi import Request
import uuid

# Mock a function similar to the endpoint
async def test_endpoint():
    print("--- Testing Dashboard Analytics with Concept ---")
    async with AsyncSessionLocal() as db:
        # 1. Get an existing tenant
        result = await db.execute(select(DashCfdiDocument.tenant_id).limit(1))
        tenant_id = result.scalar()
        if not tenant_id:
            print("No tenants or docs found.")
            return

        print(f"Testing for tenant_id: {tenant_id}")
        
        # 2. Get a random concept for this tenant
        concept_q = select(DashCfdiConcept.descripcion).join(DashCfdiDocument).where(DashCfdiDocument.tenant_id == tenant_id).limit(1)
        concept_res = await db.execute(concept_q)
        test_concept = concept_res.scalar()
        
        if not test_concept:
            print("No concepts found in DB.")
            return

        print(f"Found test concept: '{test_concept}'")

        # 3. Test total docs without filter
        q_no_filter = select(DashCfdiDocument).where(DashCfdiDocument.tenant_id == tenant_id)
        res_no_filter = await db.execute(q_no_filter)
        docs_no_filter = res_no_filter.scalars().all()
        print(f"Total docs without filter: {len(docs_no_filter)}")

        # 4. Apply concept filter
        q_with_filter = select(DashCfdiDocument).where(DashCfdiDocument.tenant_id == tenant_id).join(DashCfdiConcept).where(DashCfdiConcept.descripcion == test_concept)
        res_with_filter = await db.execute(q_with_filter)
        docs_with_filter = res_with_filter.scalars().all()
        print(f"Total docs WITH concept filter '{test_concept}': {len(docs_with_filter)}")

        # 5. Let's see if query duplicates the document (common join issue)
        print(f"Duplicates? {len(docs_with_filter) != len(set([d.cfdi_id for d in docs_with_filter]))}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
