import asyncio
import os
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database.session import get_db
from src.database.models import Cfdi

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def check():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    cfdis = (await db.execute(select(Cfdi))).scalars().all()
    for c in cfdis:
        exists = os.path.exists(c.xml_file_path)
        print(f"UUID: {c.uuid} | Path: {c.xml_file_path} | Exists: {exists}")

if __name__ == "__main__":
    asyncio.run(check())
