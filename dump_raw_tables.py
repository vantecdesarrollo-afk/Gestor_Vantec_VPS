import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, text

async def check():
    async with AsyncSessionLocal() as db:
        res_docs = await db.execute(text("SELECT cfdi_id FROM dash_cfdi_documents LIMIT 3"))
        docs = res_docs.all()
        print("Documents sample IDs:")
        for d in docs:
            print(f"- {d[0]}")
            
        res_concepts = await db.execute(text("SELECT cfdi_id, descripcion FROM dash_cfdi_concepts LIMIT 5"))
        concepts = res_concepts.all()
        print("Concepts sample:")
        for c in concepts:
            print(f"CFDI ID: {c[0]}, Desc: {c[1]}")

if __name__ == "__main__":
    asyncio.run(check())
