import sqlalchemy
from sqlalchemy import text
import sys

# Database URL from settings.DATABASE_URL but sync
DATABASE_URL = "postgresql://vantec_user:vantec_password@localhost:5432/gestor_cfdi"

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("=== TABLES ===")
        res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        for row in res:
            print(f"Table: {row[0]}")
        
        print("\n=== FOREIGN KEYS ON cfdis ===")
        fk_res = conn.execute(text("""
            SELECT
                tc.table_name, kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='cfdis';
        """))
        for row in fk_res:
            print(f"FK: {row[1]} -> {row[2]}.{row[3]}")

        print("\n=== ENTIDADES_FISCALES DATA ===")
        try:
            res = conn.execute(text("SELECT id, rfc, razon_social FROM entidades_fiscales"))
            for row in res:
                print(f"E: {row[0]} | {row[1]} | {row[2]}")
        except Exception as e:
            print(f"Table 'entidades_fiscales' error: {e}")

        print("\n=== TENANTS DATA (IF EXISTS) ===")
        try:
            res = conn.execute(text("SELECT id FROM tenants"))
            for row in res:
                print(f"T: {row[0]}")
        except Exception as e:
            print(f"Table 'tenants' error: {e}")

except Exception as global_ex:
    print(f"GLOBAL ERROR: {global_ex}")
