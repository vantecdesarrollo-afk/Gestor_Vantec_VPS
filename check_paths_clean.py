import asyncio
import sys
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import Comprobante

async def check_paths():
    with open("ruta_output.txt", "w", encoding="utf-8") as f:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Comprobante.ruta_resguardo).limit(10))
            paths = res.scalars().all()
            f.write(f"Found {len(paths)} paths\n")
            for p in paths:
                f.write(f"Path: {p}\n")

if __name__ == "__main__":
    asyncio.run(check_paths())
