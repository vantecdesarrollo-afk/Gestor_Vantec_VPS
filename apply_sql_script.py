import asyncio
from src.database.session import get_db
from sqlalchemy import text
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
        
        # Separar por bloques CREATE TABLE u otros si es necesario, 
        # pero ejecutar todo junto suele funcionar si el dialecto lo soporta.
        # En asyncpg, ejecutar bloques múltiples a veces falla si hay comandos interactivos.
        # Vamos a separar por '; ' o ';\n' para ejecutar uno a uno.
        statements = sql.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                 print(f"Ejecutando statement: {stmt[:50]}...")
                 await db.execute(text(stmt))
                 
        await db.commit()
        print("SQL aplicado con éxito.")
    except Exception as e:
        print("Error aplicando SQL:", e)
        await db.rollback()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python apply_sql_script.py <ruta_del_sql>")
    else:
        asyncio.run(apply_sql(sys.argv[1]))
