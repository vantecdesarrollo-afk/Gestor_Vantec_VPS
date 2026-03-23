import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def generate_schema():
    print("Generando DDL completo...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        # 1. Obtener todas las tablas
        res_tables = await db.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        tables = res_tables.scalars().all()
        print(f"Tablas encontradas: {tables}")
        
        with open("init.sql", "w", encoding="utf-8") as f:
            f.write("-- ==================================================================\n")
            f.write("-- DUMP DE ESTRUCTURA COMPLETA (DDL): GESTOR CFDI ON-PREMISE\n")
            f.write("-- ==================================================================\n\n")
            
            for table in tables:
                f.write(f"-- TABLA: {table.upper()}\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {table} (\n")
                
                # 2. Obtener columnas
                res_cols = await db.execute(text(
                    "SELECT column_name, data_type, character_maximum_length, "
                    "is_nullable, column_default "
                    "FROM information_schema.columns "
                    f"WHERE table_name = '{table}' "
                    "ORDER BY ordinal_position"
                ))
                cols = res_cols.all()
                
                # 3. Obtener Primary Key
                res_pk = await db.execute(text(
                    "SELECT kcu.column_name "
                    "FROM information_schema.table_constraints tc "
                    "JOIN information_schema.key_column_usage kcu "
                    "  ON tc.constraint_name = kcu.constraint_name "
                    f"WHERE tc.table_name = '{table}' AND tc.constraint_type = 'PRIMARY KEY'"
                ))
                pks = [row[0] for row in res_pk.all()]
                
                col_defs = []
                for col in cols:
                    name, dtype, max_len, is_nullable, default = col
                    type_str = dtype
                    
                    if dtype == "character varying" and max_len:
                        type_str = f"VARCHAR({max_len})"
                    elif dtype == "numeric":
                        type_str = "NUMERIC"
                    
                    null_str = "NOT NULL" if is_nullable == "NO" else ""
                    default_str = f"DEFAULT {default}" if default else ""
                    
                    pk_str = "PRIMARY KEY" if name in pks and len(pks) == 1 else ""
                    
                    line = f"    {name} {type_str} {null_str} {default_str} {pk_str}".strip()
                    if name in pks and len(pks) > 1:
                         # No poner PRIMARY KEY por columna si es compuesta
                         line = f"    {name} {type_str} {null_str} {default_str}".strip()
                         
                    col_defs.append(line)
                
                # Si hay PK compuesta
                if len(pks) > 1:
                     col_defs.append(f"    CONSTRAINT {table}_pkey PRIMARY KEY ({', '.join(pks)})")
                     
                f.write(",\n".join([f"    {c}" for c in col_defs]))
                f.write("\n);\n\n")

            # 4. Insertar datos por defecto (Default Admin)
            f.write("-- ==================================================================\n")
            f.write("-- DATOS POR DEFECTO PARA PRIMER INICIO\n")
            f.write("-- ==================================================================\n")
            f.write("INSERT INTO users (user_id, username, password_hash, is_active, is_superadmin, tenant_id) VALUES\n")
            f.write("('00000000-0000-0000-0000-000000000001', 'admin', 'pbkdf2:sha256:600000$p4O2X8uPzH87ZgR5$e8f7762696fe08cfa361664bfeb83c8d195f1fa02f690f7797825b07fb88cfeb', true, true, '00000000-0000-0000-0000-000000000001')\n")
            f.write("ON CONFLICT (username) DO NOTHING;\n\n")
            
            f.write("INSERT INTO tenants (tenant_id, rfc, business_name, is_active) VALUES\n")
            f.write("('00000000-0000-0000-0000-000000000001', 'XAXX010101000', 'Empresa Demo S.A.', true)\n")
            f.write("ON CONFLICT (rfc) DO NOTHING;\n")

        print("DDL generado en init.sql")
                
    except Exception as e:
         print("Error:", e)

if __name__ == "__main__":
    asyncio.run(generate_schema())
