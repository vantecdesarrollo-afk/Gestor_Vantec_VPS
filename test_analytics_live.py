import asyncio
from httpx import AsyncClient
from src.api.endpoints.auth import create_access_token
from datetime import timedelta

async def test_live():
    # Create a valid token with tenant_id (Use the one from debug script or DB)
    tenant_id = "550e8400-e29b-41d4-a716-446655440000" # From debug output
    username = "admin" # assumption or find in DB
    
    token = create_access_token(
        data={"sub": username, "entidad_id": tenant_id, "tenant_id": tenant_id}, 
        expires_delta=timedelta(hours=1)
    )
    print(f"Token: {token}")

    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Check dashboard
        res = await client.get("/api/v1/analytics/dashboard", headers=headers)
        print(f"\n=== DASHBOARD RESPONSE ({res.status_code}) ===")
        try:
             print(res.json())
        except Exception:
             print(res.text)

if __name__ == "__main__":
    asyncio.run(test_live())
