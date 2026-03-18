import asyncio
from httpx import AsyncClient
import os

async def test():
    # Login
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # We need a user. Let's try to query with direct DB first to see a valid user.
        print("Obtaining users from DB...")
        from src.database.session import get_db
        from src.database.models import Usuario
        from sqlalchemy import select
        
        class MockRequest:
             class State:
                  tenant_id = None
             state = State()

        db_gen = get_db(MockRequest())
        db = await anext(db_gen)
        res = await db.execute(select(Usuario))
        users = res.scalars().all()
        if not users:
             print("No users found.")
             return
            
        user = users[0]
        print(f"Testing with user: {user.username}")
        # login_and_test.py
        # Since we are inside the server, we can formulate our Request State inside a local API client trigger 
        # or just hit it from the browser layer later.
        # Let's just create a full execution of the endpoint inside FastAPI TestClient!
        from fastapi.testclient import TestClient
        from src.main import app
        
        client_test = TestClient(app)
        
        # 1. Login to trigger token
        login_res = client_test.post("/api/v1/auth/login", data={"username": user.username, "password": "temporal_password_or_real?"})
        from src.api.endpoints.auth import create_access_token
        from datetime import timedelta
        
        # Valid tenant_id found in earlier counts
        valid_tenant_id = "e6f64bb0-3971-4cc8-b883-cd183eca77d7" 
        token = create_access_token(data={"sub": user.username, "tenant_id": valid_tenant_id}, expires_delta=timedelta(hours=1))
        print("Generated Token with Tenant ID:", token)
        
        # 2. Test comprobantes
        headers = {"Authorization": f"Bearer {token}"}
        # Wait, get_active_entidad expects request.state.tenant_id set by Middleware!
        # If we hit the HTTP endpoint directly, Middleware executes!
        # But we must select a Tenant first?
        # In middleware.py, it reads token payload!
        # Does the token payload have tenant_id?
        # Let's verify middleware.py!
        
        res_comp = client_test.get("/api/v1/comprobantes", headers=headers)
        print("GET /api/v1/comprobantes Status:", res_comp.status_code)
        if res_comp.status_code == 200:
             print("Data length:", len(res_comp.json()))
        else:
             print("Response:", res_comp.text)

        # 3. Test Admin
        res_admin = client_test.get("/api/v1/admin/entidades", headers=headers)
        print("GET /api/v1/admin/entidades Status:", res_admin.status_code)
        if res_admin.status_code == 200:
             print("Admin Entities length:", len(res_admin.json()))
        else:
             print("Admin response:", res_admin.text)

if __name__ == "__main__":
    asyncio.run(test())
