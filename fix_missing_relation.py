import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def fix_missing_relation_by_id():
    async with AsyncSessionLocal() as session:
        try:
            print("Updating relation row 519 with valid cfdi_id by exact ID...")
            res = await session.execute(
                text("""
                    UPDATE cfdi_relacionados 
                    SET cfdi_id = :cid 
                    WHERE id = 519
                """),
                {
                    "cid": "5c50b007-7b1b-4cb1-b21a-2363acfb4daa" # ID from relation 518
                }
            )
            await session.commit()
            print(f"Update executed. Rows affected: {res.rowcount}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_missing_relation_by_id())
