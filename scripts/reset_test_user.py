import asyncio
import os
import sys
from sqlalchemy import select
from passlib.context import CryptContext

# Root path
sys.path.append(os.getcwd())

from src.database.session import AsyncSessionLocal
from src.database.models import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def ensure_test_user():
    async with AsyncSessionLocal() as db:
        print("🔍 Checking test user...")
        email = "test@vantec.com"
        result = await db.execute(select(Usuario).where(Usuario.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"➕ Creating test user: {email}")
            user = Usuario(
                username="test_user",
                email=email,
                hashed_password=get_password_hash("Vantec2026"),
                is_active=True,
                is_superadmin=True
            )
            db.add(user)
        else:
            print(f"🔄 Updating password for: {email}")
            user.hashed_password = get_password_hash("Vantec2026")
            user.is_active = True
        
        await db.commit()
        print("✅ Success! Credentials: test@vantec.com / Vantec2026")

if __name__ == "__main__":
    asyncio.run(ensure_test_user())
