import asyncio
import uuid
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import User
from src.api.endpoints.auth import create_access_token

async def main():
    async with AsyncSessionLocal() as db:
        try:
            res = await db.execute(select(User).limit(1))
            user = res.scalar_one_or_none()
            if user:
                token = create_access_token(data={
                    "sub": str(user.user_id),
                    "username": user.username,
                    "entidad_id": str(user.tenant_id),
                    "tenant_id": str(user.tenant_id),
                    "is_superadmin": user.is_superadmin,
                    "entidades": [{ "id": str(user.tenant_id), "rfc": "VCO1307234VA", "rol": "ADMIN" }]
                })
                with open("/tmp/token.txt", "w") as f:
                    f.write(f"TOKEN|{token}\nENTIDAD|{user.tenant_id}")
                print("Saved")
            else:
                print("No users found")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
