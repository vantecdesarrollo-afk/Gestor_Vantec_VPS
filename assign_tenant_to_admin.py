import asyncio
from sqlalchemy import select, update
from src.database.session import get_db
from src.database.models import User, Comprobante

class MockRequest:
    class State:
         tenant_id = None
    state = State()

async def run():
    db_gen = get_db(MockRequest())
    db = await anext(db_gen)
    
    # 1. Find a Comprobante to extract its entidad_id
    res_comp = await db.execute(select(Comprobante).limit(1))
    comp = res_comp.scalar_one_or_none()
    if not comp:
         print("No Comprobante found to extract tenant_id.")
         return
         
    target_tenant = comp.entidad_id
    print(f"Target Tenant from Comprobante: {target_tenant}")

    # 2. Find admin user
    res_user = await db.execute(select(User).where(User.username == "admin"))
    user = res_user.scalar_one_or_none()
    if not user:
         print("User 'admin' not found.")
         return
         
    # 3. Update admin's tenant_id
    print(f"Updating user: {user.username} (ID: {user.user_id}) -> tenant_id: {target_tenant}")
    await db.execute(
         update(User)
         .where(User.user_id == user.user_id)
         .values(tenant_id=target_tenant)
    )
    await db.commit()
    print("Admin user updated successfully.")

if __name__ == "__main__":
    asyncio.run(run())
