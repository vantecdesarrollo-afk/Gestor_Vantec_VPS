import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext
from src.database.models import User, Base
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_admin():
    print("-" * 60)
    print("  [VANTEC] INYECTOR DE SEMILLA VCORE v5.0.1 - GOLD MASTER")
    print("-" * 60)
    
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        try:
            # Sincronización final
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            result = await session.execute(select(User).where(User.username == "admin"))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("[!] Actualizando privilegios de 'admin'...")
                existing_user.rol = "SUPERADMIN"
                existing_user.is_superadmin = True
            else:
                print("[+] Inyectando Admin con Poder de SUPERADMIN...")
                new_admin = User(
                    user_id=uuid.uuid4(),
                    username="admin",
                    password_hash=pwd_context.hash("admin123"),
                    email="admin@vantec.com",
                    is_superadmin=True,
                    is_active=True,
                    rol="SUPERADMIN" 
                )
                session.add(new_admin)
            
            await session.commit()
            print("[SUCCESS] Sistema desbloqueado al 100%.")
            
        except Exception as e:
            print(f"[ERROR]: {str(e)}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_admin())