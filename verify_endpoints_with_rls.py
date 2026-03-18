import asyncio
import uuid
from sqlalchemy import text
from src.database.session import AsyncSessionLocal
from src.api.endpoints.analytics import get_dashboard_analytics
from src.api.endpoints.cfdis import get_cfdis

async def verify_endpoints_with_rls():
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    entidad_id = uuid.UUID(entidad_id_str)
    
    log(f"Simulating API calls for Entidad ID: {entidad_id}")
    
    async with AsyncSessionLocal() as session:
        log("Injecting RLS context...")
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id_str}
        )
        
        log("\n=== Testing Dashboard Analytics ===")
        try:
            dashboard_result = await get_dashboard_analytics(db=session, entidad_id=entidad_id)
            log("Dashboard Result:")
            for k, v in dashboard_result.items():
                log(f"  {k}: {v}")
        except Exception as e:
            log(f"Error in dashboard: {e}")
            
        log("\n=== Testing CFDIS Explorer ===")
        try:
            cfdis_result = await get_cfdis(db=session, entidad_id=entidad_id)
            log(f"Total documents returned: {len(cfdis_result)}")
            
            for doc in cfdis_result:
                log(f"  Folio: {doc.get('folio')}, UUID: {doc.get('uuid')}, Total: {doc.get('total')}")
                reps = doc.get("reps_asociados", [])
                log(f"    Reps asociados count: {len(reps)}")
                for r in reps:
                    log(f"      - Rep UUID: {r.get('uuid')}, Total: {r.get('total')}")
                    
        except Exception as e:
            log(f"Error in cfdis: {e}")
            
    with open("verify_endpoints_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(verify_endpoints_with_rls())
