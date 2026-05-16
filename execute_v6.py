import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def run_sql(sql_file):
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "prueba01")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "gestor_cfdi")
    
    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_async_engine(db_url)
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        async with engine.begin() as conn:
            # Separamos por punto y coma, que es el estándar de SQL.
            # En este archivo no hay PL/SQL complejo que rompa el split.
            statements = sql.split(';')
            for stmt in statements:
                clean_stmt = stmt.strip()
                if not clean_stmt: continue
                await conn.execute(text(clean_stmt))
            print("✅ SQL Executed Successfully.")
    except Exception as e:
        print(f"❌ Error Executing SQL: {str(e)}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_sql('c:/Test_Antigravity/Gestor_CFDI_Vantec/08_VANTEC_FINANCIAL_INTEGRITY_L6.sql'))
