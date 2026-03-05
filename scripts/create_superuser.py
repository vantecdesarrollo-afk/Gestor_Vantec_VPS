import asyncio
import os
import sys
from sqlalchemy import select
from passlib.context import CryptContext

# Asegurar que el path incluya la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.session import AsyncSessionLocal
from src.database.models import User, Tenant

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_superuser():
    async with AsyncSessionLocal() as db:
        print("--- Inicializando Datos Maestros Vantec ---")
        
        # 1. Verificar o Crear Tenant
        tenant_rfc = "VAN010101ABC"
        result = await db.execute(select(Tenant).where(Tenant.rfc == tenant_rfc))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            print("Creando Tenant: Vantec Consultores...")
            tenant = Tenant(
                rfc=tenant_rfc,
                business_name="Vantec Consultores S.A. de C.V.",
                is_active=True
            )
            db.add(tenant)
            await db.flush() # Para obtener el tenant_id generado
        else:
            print(f"Tenant '{tenant.business_name}' ya existe.")

        # 2. Verificar o Crear Usuario Admin
        username = "admin"
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"Creando Usuario: {username}...")
            user = User(
                username=username,
                email="admin@vantec.mx",
                password_hash=get_password_hash("Vantec2026"),
                tenant_id=tenant.tenant_id,
                is_active=True,
                auth_provider="LOCAL"
            )
            db.add(user)
            print(f"¡Éxito! Usuario '{username}' creado exitosamente para el tenant {tenant.business_name}.")
        else:
            print(f"Usuario '{username}' ya existe.")

        await db.commit()
        print("------------------------------------------")

if __name__ == "__main__":
    asyncio.run(create_superuser())
