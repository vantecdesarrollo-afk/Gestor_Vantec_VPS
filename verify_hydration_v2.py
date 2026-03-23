import asyncio
from src.database.session import get_db
from sqlalchemy import text

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def verify_count():
    log = []
    log.append("Verificando inserciones...")
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    try:
        res_doc = await db.execute(text("SELECT count(*) FROM dash_cfdi_documents"))
        count_doc = res_doc.scalar()
        
        res_concept = await db.execute(text("SELECT count(*) FROM dash_cfdi_concepts"))
        count_concept = res_concept.scalar()
        
        log.append(f"dash_cfdi_documents: {count_doc}")
        log.append(f"dash_cfdi_concepts: {count_concept}")
        
        if count_doc > 0:
             log.append("✅ Hidratación exitosa.")
        else:
             log.append("⚠️ No se insertaron documentos.")
    except Exception as e:
        log.append(f"Error verificando: {e}")

    with open("verify_hydration_log.txt", "w", encoding="utf-8") as f:
         f.write("\n".join(log))
         print("Log guardado en verify_hydration_log.txt")

if __name__ == "__main__":
    asyncio.run(verify_count())
