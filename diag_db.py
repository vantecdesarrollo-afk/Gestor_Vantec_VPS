
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_conn():
    url = "postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi"
    print(f"Testing: {url}")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT id FROM entidades_fiscales LIMIT 1"))
            row = res.fetchone()
            if row:
                print(f"ID_ENCONTRADO: {row[0]}")
            else:
                print("ID_ENCONTRADO: NOTFOUND")
        await engine.dispose()
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_conn())
