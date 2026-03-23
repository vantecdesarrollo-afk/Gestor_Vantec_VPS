import sqlalchemy
from sqlalchemy import create_engine, inspect

DATABASE_URL = "postgresql://postgres:prueba01@localhost:5432/gestor_cfdi"

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with open("users_columns.txt", "w", encoding="utf-8") as f:
        columns = inspector.get_columns('users')
        for c in columns:
            f.write(f"{c['name']}: {c['type']}\n")

except Exception as e:
    print(f"Error: {e}")
