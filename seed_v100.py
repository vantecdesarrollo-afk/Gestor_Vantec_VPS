import asyncio
from src.database.session import AsyncSessionLocal
from src.database.models import User, Tenant
from sqlalchemy import select
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def test():
    async with AsyncSessionLocal() as db:
        # 1. Buscar Tenant de Vantec
        tenant = (await db.execute(select(Tenant).where(Tenant.rfc == 'VCO1307234VA'))).scalar_one_or_none()
        if not tenant:
             tenant = Tenant(
                  tenant_id=uuid.uuid4(),
                  rfc='VCO1307234VA',
                  business_name='Vantec Consultores'
             )
             db.add(tenant)
             await db.flush()

        # 2. Guardar admin asociado a este Tenant
        user = (await db.execute(select(User).where(User.username == 'admin'))).scalar_one_or_none()
        if not user:
             user = User(
                  user_id=uuid.uuid4(),
                  tenant_id=tenant.tenant_id,
                  username='admin',
                  email='admin@vantec.mx',
                  password_hash=pwd_context.hash('admin123'),
                  is_active=True
             )
             db.add(user)
             print("✅ Admin user created directly pinned to Tenant.")
        else:
             user.tenant_id = tenant.tenant_id
             user.password_hash = pwd_context.hash('admin123')
             print("✅ Admin user linked to Tenant.")

        await db.commit()
        print("✅ Seeding complete.")

if __name__ == "__main__":
    asyncio.run(test())
