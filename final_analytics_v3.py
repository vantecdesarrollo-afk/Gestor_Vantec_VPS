import asyncio
import uuid
from sqlalchemy import text
from src.database.session import AsyncSessionLocal
from src.api.endpoints.analytics import get_dashboard_analytics

async def verify_final():
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    entidad_id = uuid.UUID(entidad_id_str)
    output = []
    def log(msg):
        output.append(str(msg))
        print(msg)
        
    log(f"Testing active dashboard analytics...")
    
    async with AsyncSessionLocal() as session:
        log("\n=== WITHOUT RLS Context ===")
        try:
            res = await get_dashboard_analytics(db=session, entidad_id=entidad_id)
            log("Dashboard Result (No RLS):")
            for k, v in res.items():
                log(f"  {k}: {v}")
        except Exception as e:
             log(f"Error: {e}")
             
        log("\n=== WITH RLS Context ===")
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id_str}
        )
        try:
            res = await get_dashboard_analytics(db=session, entidad_id=entidad_id)
            log("Dashboard Result (With RLS):")
            for k, v in res.items():
                log(f"  {k}: {v}")
        except Exception as e:
             log(f"Error: {e}")
             
    with open("final_analytics_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(verify_final())
