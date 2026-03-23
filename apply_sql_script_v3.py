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
    log_messages = []
    log_messages.append(f"Aplicando {file_path}...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        
        statements = sql.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                 stmt_clean = stmt[:50].replace('\n', ' ')
                 log_messages.append(f"Ejecutando statement: {stmt_clean}...")
                 try:
                     await db.execute(text(stmt))


                 except Exception as inner_e:
                     log_messages.append(f"Error en statement: {stmt[:50]}")
                     log_messages.append(str(inner_e))
                     raise inner_e
                     
        await db.commit()
        log_messages.append("SQL aplicado con éxito.")
    except Exception as e:
        log_messages.append("Error general aplicando SQL:")
        log_messages.append(traceback.format_exc())
        await db.rollback()
    
    with open("apply_output.txt", "w", encoding="utf-8") as f:
         f.write("\n".join(log_messages))
         print("Log guardado en apply_output.txt")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python apply_sql_script.py <ruta_del_sql>")
    else:
        asyncio.run(apply_sql(sys.argv[1]))
