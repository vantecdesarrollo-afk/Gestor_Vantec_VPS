import asyncio
from src.database.session import get_db
from src.database.models import User, Tenant
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MockRequest:
    class State:
        tenant_id = None
    state = State()

async def create_user():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    
    # 1. Buscar tenant
    res = await db.execute(select(Tenant))
    tenant = res.scalars().first()
    if not tenant:
        print("No hay tenants en la base de datos.")
        return
        
    # 2. Verificar si ya existe
    res_u = await db.execute(select(User).where(User.username == "test_agent"))
    existing = res_u.scalar_one_or_none()
    
    if existing:
        print("Usuario test_agent ya existe.")
        return
        
    # 3. Crear usuario
    hashed = pwd_context.hash("admin")
    new_user = User(
        username="test_agent",
        password_hash=hashed,
        email="test@test.com",
        tenant_id=tenant.tenant_id,
        is_active=True,
        is_superadmin=True
    )
    db.add(new_user)
    await db.commit()
    print("✅ Usuario test_agent creado con contraseña 'admin'.")

if __name__ == "__main__":
    asyncio.run(create_user())
