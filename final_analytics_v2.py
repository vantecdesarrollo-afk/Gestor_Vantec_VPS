import asyncio
import uuid
from sqlalchemy import text
from src.database.session import AsyncSessionLocal
from src.api.endpoints.analytics import get_dashboard_analytics

async def verify_final():
    entidad_id_str = "e6f64bb0-3971-4cc8-b883-cd183eca77d7"
    entidad_id = uuid.UUID(entidad_id_str)
    
    print(f"Testing active dashboard analytics...")
    
    async with AsyncSessionLocal() as session:
        # DO NOT inject RLS context so that we see all relations for this test dataset 
        # (effectively simulating superuser dashboard OR bypassing RLS limits for verification setup)
        # Wait, get_db DOES inject it! But our script does not inject unless we call it.
        # If we DON'T inject, the raw SQL inside analytics.py runs without app.current_tenant_id!
        # Let's test both ways just to be sure!
        
        print("\n=== WITHOUT RLS Context ===")
        try:
            res = await get_dashboard_analytics(db=session, entidad_id=entidad_id)
            print("Dashboard Result (No RLS):")
            for k, v in res.items():
                print(f"  {k}: {v}")
        except Exception as e:
             print(f"Error: {e}")
             
        print("\n=== WITH RLS Context ===")
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": entidad_id_str}
        )
        try:
            res = await get_dashboard_analytics(db=session, entidad_id=entidad_id)
            print("Dashboard Result (With RLS):")
            for k, v in res.items():
                print(f"  {k}: {v}")
        except Exception as e:
             print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_final())
