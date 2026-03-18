import asyncio
import traceback
from src.database.session import AsyncSessionLocal
from src.database.models import User, Tenant
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password,  hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def test():
    with open("login_backend_test.log", "w", encoding="utf-8") as f:
         try:
              async with AsyncSessionLocal() as db:
                   # 1. Buscar usuario
                   query = select(User).where((User.username == 'admin') | (User.email == 'admin'))
                   result = await db.execute(query)
                   user = result.scalar_one_or_none()

                   if not user:
                        f.write("❌ User not found\n")
                        return

                   f.write(f"✅ User found: {user.username}\n")

                   # 2. Verificar password
                   if not user.password_hash or not verify_password('admin123', user.password_hash):
                        f.write("❌ Password incorrect\n")
                        return

                   f.write("✅ Password correct\n")

                   # 3. Cargar Tenant
                   tenant_query = select(Tenant).where(Tenant.tenant_id == user.tenant_id)
                   t_result = await db.execute(tenant_query)
                   tenant = t_result.scalar_one_or_none()

                   if tenant:
                        f.write(f"✅ Tenant found: {tenant.rfc}\n")
                   else:
                        f.write("❌ Tenant not found\n")

                   # 4. JWT o similar (simulado)
                   f.write("✅ End of logic simulated successfully.\n")

         except Exception:
              f.write("❌ Crash:\n")
              f.write(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test())
