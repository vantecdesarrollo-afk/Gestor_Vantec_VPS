import asyncio
import uuid
import traceback
from src.database.session import AsyncSessionLocal
from src.api.endpoints.comprobantes import get_comprobantes

async def test_endpoint():
    async with AsyncSessionLocal() as db:
        try:
            entidad_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
            res = await get_comprobantes(db=db, entidad_id=entidad_id, limit=50, offset=0)
            print("Response successfully loaded:", len(res), "items")
        except Exception as e:
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
