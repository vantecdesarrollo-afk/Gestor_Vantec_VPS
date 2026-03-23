import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def verify_count():
    print("Verificando inserciones...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        res_doc = await db.execute(text("SELECT count(*) FROM dash_cfdi_documents"))
        count_doc = res_doc.scalar()
        
        res_concept = await db.execute(text("SELECT count(*) FROM dash_cfdi_concepts"))
        count_concept = res_concept.scalar()
        
        print(f"dash_cfdi_documents: {count_doc}")
        print(f"dash_cfdi_concepts: {count_concept}")
        
        if count_doc > 0:
             print("✅ Hidratación exitosa.")
        else:
             print("⚠️ No se insertaron documentos.")
    except Exception as e:
        print("Error verificando:", e)

if __name__ == "__main__":
    asyncio.run(verify_count())
