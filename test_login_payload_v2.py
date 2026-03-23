import asyncio
from httpx import AsyncClient

async def test_login():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        res = await client.post("/api/v1/auth/login", data={"username": "admin", "password": "prueba01"})
        print(f"=== LOGIN STATUS: {res.status_code} ===")
        if res.status_code == 200:
             data = res.json()
             token = data.get("access_token")
             print(f"Token acquired!")
             import jwt
             # Decode offline to see payload without secret (verify contents)
             payload = jwt.decode(token, options={"verify_signature": False})
             print("\n=== TOKEN PAYLOAD ===")
             print(f"Username: {payload.get('username')}")
             print(f"Is Superadmin: {payload.get('is_superadmin')}")
             print(f"Entidades List: {payload.get('entidades')}")
        else:
             print(f"Error: {res.text}")

if __name__ == "__main__":
    asyncio.run(test_login())
