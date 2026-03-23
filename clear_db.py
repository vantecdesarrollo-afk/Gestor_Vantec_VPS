import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def clear_tables():
    print("Vaciando tablas para pruebas...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        # Desactivar FK para truncar de forma masiva
        await db.execute(text("TRUNCATE TABLE dash_cfdi_concepts CASCADE;"))
        await db.execute(text("TRUNCATE TABLE dash_cfdi_documents CASCADE;"))
        await db.execute(text("TRUNCATE TABLE cfdi_relacionados CASCADE;"))
        await db.execute(text("TRUNCATE TABLE comprobantes CASCADE;"))
        await db.execute(text("TRUNCATE TABLE cfdis CASCADE;"))
        await db.commit()
        print("✅ Tablas vaciadas con éxito.")
    except Exception as e:
        print("Error vaciando tablas:", e)
        await db.rollback()

if __name__ == "__main__":
    asyncio.run(clear_tables())
