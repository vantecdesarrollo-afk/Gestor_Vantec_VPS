import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def dump_schema():
    print("Iniciando dump de esquema...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        # 1. Obtener todas las tablas
        res_tables = await db.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        ))
        tables = [row[0] for row in res_tables.all()]
        print(f"Tablas encontradas: {tables}")
        
        with open("schema_dump.txt", "w", encoding="utf-8") as f:
            f.write("-- ==========================================\n")
            f.write("-- DUMP DE ESQUEMA (SOLO ESTRUCTURA)\n")
            f.write("-- ==========================================\n\n")
            
            for table in tables:
                f.write(f"-- TABLA: {table}\n")
                f.write(f"CREATE TABLE {table} (\n")
                
                # 2. Obtener columnas
                res_cols = await db.execute(text(
                    "SELECT column_name, data_type, character_maximum_length, is_nullable, column_default "
                    "FROM information_schema.columns "
                    f"WHERE table_name = '{table}' "
                    "ORDER BY ordinal_position"
                ))
                cols = res_cols.all()
                
                col_defs = []
                for col in cols:
                    name, dtype, max_len, is_nullable, default = col
                    type_str = dtype
                    if max_len:
                        type_str += f"({max_len})"
                    
                    if name == "user_id" or name == "cfdi_id": # UUIDs
                         # En DB se ve como USER-DEFINED o similar si es UUID
                         pass
                         
                    null_str = "NOT NULL" if is_nullable == "NO" else ""
                    default_str = f"DEFAULT {default}" if default else ""
                    
                    line = f"    {name} {type_str} {null_str} {default_str}".strip()
                    col_defs.append(line)
                
                f.write(",\n".join([f"    {c}" for c in col_defs]))
                f.write("\n);\n\n")
                
        print("Esquema guardado en schema_dump.txt")
    except Exception as e:
        print("Error en dump:", e)

if __name__ == "__main__":
    asyncio.run(dump_schema())
