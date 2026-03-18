import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def check():
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(text("SELECT * FROM cfdi_relacionados"))
            rows = res.fetchall()
            log(f"Total rows in cfdi_relacionados: {len(rows)}")
            for r in rows:
                log(r)
        except Exception as e:
            log(f"Error: {e}")
            
    with open("check_all_relaciones_output_v2.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(check())
