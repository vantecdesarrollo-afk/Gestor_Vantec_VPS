import asyncio
from src.database.session import get_db
from sqlalchemy import text
import traceback
import sys

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def apply_sql(file_path: str):
    print(f"Aplicando {file_path}...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        
        statements = sql.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                 print(f"Ejecutando statement: {stmt[:50]}...")
                 try:
                     await db.execute(text(stmt))
                 except Exception as inner_e:
                     print(f"Error en statement: {stmt[:50]}")
                     print(inner_e)
                     raise inner_e # Re-raise to trigger rollback
                     
        await db.commit()
        print("SQL aplicado con éxito.")
    except Exception as e:
        print("Error general aplicando SQL:")
        traceback.print_exc()
        await db.rollback()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python apply_sql_script.py <ruta_del_sql>")
    else:
        asyncio.run(apply_sql(sys.argv[1]))
