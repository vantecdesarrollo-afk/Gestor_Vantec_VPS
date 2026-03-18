import asyncio
from sqlalchemy import text
from src.database.session import AsyncSessionLocal

async def audit():
    async with AsyncSessionLocal() as session:
        # RESET RLS to read everything
        await session.execute(text("RESET app.current_tenant_id"))
        
        result = await session.execute(text("SELECT * FROM cfdi_relacionados"))
        rows = result.fetchall()
        import json
        output_data = {
            "all_relations": [{"id": r[0], "cfdi_id": r[1], "padre": r[2], "relacionado": r[3], "tipo": r[4]} for r in rows]
        }
        with open("C:\\Test_Antigravity\\Gestor_CFDI_Vantec\\audit_relations_output.json", "w") as f:
            json.dump(output_data, f, indent=4)
        print("JSON SAVED")

if __name__ == "__main__":
    asyncio.run(audit())
