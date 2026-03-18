import asyncio
import json
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def test():
    db = AsyncSessionLocal()
    try:
        result = await db.execute(text('SELECT * FROM cfdis LIMIT 1'))
        cols = list(result.keys())
        with open('columns.txt', 'w') as f:
            f.write(json.dumps(cols))
    except Exception as e:
        with open('columns.txt', 'w') as f:
            f.write(str(e))
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(test())
