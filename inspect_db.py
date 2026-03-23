import sqlalchemy
from sqlalchemy import create_engine, inspect

DATABASE_URL = "postgresql://postgres:prueba01@localhost:5432/gestor_cfdi"

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    print("=== Columns in comprobantes ===")
    columns = inspector.get_columns('comprobantes')
    for c in columns:
        print(f"{c['name']}: {c['type']}")
        
    print("\n=== Columns in cfdi_relacionados ===")
    columns = inspector.get_columns('cfdi_relacionados')
    for c in columns:
        print(f"{c['name']}: {c['type']}")

except Exception as e:
    print(f"Error: {e}")
