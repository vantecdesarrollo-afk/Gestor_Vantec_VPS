
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def get_id():
    engine = create_async_engine('postgresql+asyncpg://postgres:prueba01@localhost:5432/gestor_cfdi')
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT id, nombre FROM entidades_fiscales LIMIT 1'))
        row = res.fetchone()
        if row:
            print(f"ID: {row[0]}, NOMBRE: {row[1]}")
        else:
            print("NOTFOUND")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(get_id())
