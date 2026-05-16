import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext
from src.database.models import User, Base
from src.core.config import settings

# 1. Configuración de Seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def seed_admin():
    print("-----------------------------------------------------------")
    print("  [VANTEC] INYECTOR DE SEMILLA VCORE v5.0.1")
    print("-----------------------------------------------------------")
    
    # Usamos la DATABASE_URL del entorno actual (que debería ser vcore_blank_db en el Sandbox)
    print(f"[+] Conectando a: {settings.DATABASE_URL}")
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        try:
            # 2. Asegurar que las tablas existen (SQLAlchemy autogenerate)
            print("[+] Verificando/Creando tablas de base de datos...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # 3. Buscar si el admin ya existe
            result = await session.execute(select(User).where(User.username == "admin"))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("[!] El usuario 'admin' ya existe. Actualizando credenciales...")
                existing_user.password_hash = get_password_hash("admin123")
                existing_user.is_superadmin = True
                existing_user.is_active = True
            else:
                print("[+] Inyectando Super Usuario Administrador...")
                new_admin = User(
                    user_id=uuid.uuid4(),
                    username="admin",
                    password_hash=get_password_hash("admin123"),
                    email="admin@vantec.com",
                    is_superadmin=True,
                    is_active=True,
                    rol="ADMIN"
                )
                session.add(new_admin)
            
            await session.commit()
            print("[SUCCESS] Super Administrador (admin / admin123) inyectado exitosamente.")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Fallo en la inyección de semilla: {str(e)}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_admin())
