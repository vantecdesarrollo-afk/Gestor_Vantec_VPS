import asyncio
from sqlalchemy import select
from src.database.session import AsyncSessionLocal
from src.database.models import User, Tenant
from src.api.endpoints.auth import create_access_token

async def test_direct():
    with open("test_login_payload_direct.txt", "w", encoding="utf-8") as f:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(User).limit(1))
            user = res.scalar()
            if not user:
                 f.write("No users found\n")
                 return
                 
            is_superadmin = getattr(user, "is_superadmin", False)
            f.write(f"User: {user.username}, Is Superadmin: {is_superadmin}\n")

            entidades = []
            if is_superadmin:
                 e_res = await db.execute(select(Tenant))
                 entidades = e_res.scalars().all()
            else:
                 e_res = await db.execute(select(Tenant).where(Tenant.tenant_id == user.tenant_id))
                 entidades = e_res.scalars().all()

            entidades_json = [{
                 "id": str(e.tenant_id),
                 "rfc": e.rfc,
                 "razon_social": e.business_name
            } for e in entidades]

            data = {
                 "sub": str(user.user_id), 
                 "username": user.username,
                 "is_superadmin": is_superadmin,
                 "entidades": entidades_json
            }
            
            token = create_access_token(data=data)
            import jwt
            payload = jwt.decode(token, options={"verify_signature": False})
            f.write("\n=== PAYLOAD DECODE ===\n")
            f.write(str(payload) + "\n")

if __name__ == "__main__":
    asyncio.run(test_direct())
