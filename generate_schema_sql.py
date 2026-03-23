import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def generate_schema():
    print("Generando DDL...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        # Tablas de interés
        tables_of_interest = ["cfdis", "comprobantes", "cfdi_relacionados", "cfdi_metadata"]
        
        with open("schema_emision_cfdi.sql", "w", encoding="utf-8") as f:
            f.write("-- ==================================================================\n")
            f.write("-- DUMP DE ESTRUCTURA (DDL): CFDI, EMISIÓN, CONCEPTOS, MONEDAS\n")
            f.write("-- ==================================================================\n\n")
            
            for table in tables_of_interest:
                f.write(f"-- TABLA: {table.upper()}\n")
                f.write(f"CREATE TABLE {table} (\n")
                
                # 1. Obtener columnas
                res_cols = await db.execute(text(
                    "SELECT column_name, data_type, character_maximum_length, "
                    "is_nullable, column_default "
                    "FROM information_schema.columns "
                    f"WHERE table_name = '{table}' "
                    "ORDER BY ordinal_position"
                ))
                cols = res_cols.all()
                
                # 2. Obtener Primary Key
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
                        type_str = "NUMERIC" # Podríamos intentar sacar precisión, pero NUMERIC es válido
                    
                    null_str = "NOT NULL" if is_nullable == "NO" else ""
                    default_str = f"DEFAULT {default}" if default else ""
                    
                    pk_str = "PRIMARY KEY" if name in pks and len(pks) == 1 else ""
                    
                    line = f"    {name} {type_str} {null_str} {default_str} {pk_str}".strip()
                    col_defs.append(line)
                
                # Si hay PK compuesta
                if len(pks) > 1:
                     col_defs.append(f"    CONSTRAINT {table}_pkey PRIMARY KEY ({', '.join(pks)})")
                     
                f.write(",\n".join([f"    {c}" for c in col_defs]))
                f.write("\n);\n\n")
                
                f.write(f"-- NOTA DE CONCEPTOS EN {table.upper()}:\n")
                if table == "cfdis":
                    f.write("-- Los conceptos no tienen tabla dedicada. Se asume que se procesan del XML en `metadata_xml` (jsonb).\n\n")
                elif table == "comprobantes":
                    f.write("-- Esta tabla posee `moneda` y `tipo_cambio` para el listado básico.\n\n")
                f.write("\n")
                
        print("DDL generado en schema_emision_cfdi.sql")
                
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(generate_schema())
