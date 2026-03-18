import asyncio
from src.database.session import get_db
from src.database.models import Cfdi, Comprobante, Usuario, Tenant
from sqlalchemy import select

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def count_rows():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        cfdi_cnt = len((await db.execute(select(Cfdi))).scalars().all())
        comp_cnt = len((await db.execute(select(Comprobante))).scalars().all())
        user_cnt = len((await db.execute(select(Usuario))).scalars().all())
        tenant_cnt = len((await db.execute(select(Tenant))).scalars().all())
        with open("rows_count.txt", "w") as f:
             f.write(f"Cfdi: {cfdi_cnt}\n")
             f.write(f"Comprobante: {comp_cnt}\n")
             f.write(f"Usuario: {user_cnt}\n")
             f.write(f"Tenant: {tenant_cnt}\n")
        print("Written counts.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(count_rows())
