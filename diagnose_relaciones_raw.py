import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def diagnose_raw_sql():
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(text("SELECT count(*) FROM cfdi_relacionados"))
            count = res.scalar()
            log(f"Total cfdi_relacionados in DB (Raw SQL): {count}")
            
            comp_uuids = [
                'd2a9308b-f4d9-4357-8adf-de186a7ef5d1', # Folio 303
                'af41872d-1e12-44ec-9d58-614b23e9655c', # Folio 305
                'd1d1f7d4-7683-4f46-a545-5e08c907cb11', # Folio 800
                '39e5e6e4-534a-4b08-a5ae-77a6e3b41c91', # Folio 804
                '24a75e3b-261f-455a-9d04-b30be95865bd'  # Folio 813
            ]
            
            log("\nSearching for related UUIDs...")
            matches_count = 0
            for u in comp_uuids:
                log(f"\nSearching for UUID: {u}")
                res = await session.execute(
                    text("SELECT * FROM cfdi_relacionados WHERE uuid_padre ILIKE :u OR uuid_relacionado ILIKE :u"),
                    {"u": u}
                )
                matches = res.fetchall()
                log(f"  Matches for {u}: {len(matches)}")
                for m in matches:
                    matches_count += 1
                    log(f"    {m}")
                    
            log(f"\nTotal matches found: {matches_count}")
                    
        except Exception as e:
            log(f"Error: {e}")
            
    with open("diagnose_relaciones_raw_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(diagnose_raw_sql())
