import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def inspect():
    try:
        async with AsyncSessionLocal() as session:
            # Prender RLS o RESET
            await session.execute(text("RESET app.current_tenant_id"))
            
            res1 = await session.execute(text("SELECT id, uuid, folio, tipo_comprobante FROM comprobantes"))
            rows1 = res1.fetchall()

            res2 = await session.execute(text("SELECT id, uuid, folio, tipo_comprobante FROM cfdis"))
            rows2 = res2.fetchall()
            
            import json
            output_data = {
                "comprobantes": [{"id": r[0], "uuid": str(r[1]), "folio": r[2], "tipo": r[3]} for r in rows1],
                "cfdis": [{"id": r[0], "uuid": str(r[1]), "folio": r[2], "tipo": r[3]} for r in rows2]
            }
            with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\inspect_uuids_output.json", "w") as f:
                json.dump(output_data, f, indent=4)
            print("JSON SAVED")
    except Exception as e:
         with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\inspect_error.txt", "w") as f:
             f.write(str(e))
         print(f"Error saved: {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
