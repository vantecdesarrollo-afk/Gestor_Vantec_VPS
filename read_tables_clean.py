import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def list_tables():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    output = []
    try:
        res = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = res.scalars().all()
        output.append(f"Tables found: {tables}\n")
        for t in tables:
             res_cols = await db.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'"))
             cols = res_cols.all()
             output.append(f"--- Table {t} ---")
             for c in cols:
                  output.append(f"  {c[0]} ({c[1]})")
             output.append("")
        
        with open("tables_detailed_clean.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print("Written to tables_detailed_clean.txt")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(list_tables())
