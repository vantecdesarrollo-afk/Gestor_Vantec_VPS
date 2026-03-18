import asyncio
import traceback
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def test():
    db = AsyncSessionLocal()
    try:
        result = await db.execute(text('SELECT * FROM cfdis LIMIT 1'))
        print("Columns in DB:", result.keys())
    except Exception as e:
        print(traceback.format_exc())
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(test())
