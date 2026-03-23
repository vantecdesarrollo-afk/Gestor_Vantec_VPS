import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, text

async def check():
    async with AsyncSessionLocal() as db:
        # Check all concepts
        res = await db.execute(text("SELECT concept_id, cfdi_id, descripcion FROM dash_cfdi_concepts"))
        rows = res.all()
        print(f"Testing {len(rows)} concepts:")
        for r in rows:
            print(f"ID: {r[0]}, CFDI_ID: {r[1]}, DESC: {r[2]}")

if __name__ == "__main__":
    asyncio.run(check())
