import asyncio
import os
import sys

sys.path.insert(0, r"C:\Test_Antigravity\Gestor_CFDI_Vantec")

from src.database.session import AsyncSessionLocal
from sqlalchemy import select, text

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT concept_id, cfdi_id, descripcion FROM dash_cfdi_concepts"))
        rows = res.all()
        
        with open("direct_concepts.txt", "w", encoding="utf-8") as f:
            f.write(f"Testing {len(rows)} concepts:\n")
            for r in rows:
                f.write(f"ID: {r[0]}, CFDI_ID: {r[1]}, DESC: {r[2]}\n")

if __name__ == "__main__":
    asyncio.run(check())
