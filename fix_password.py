import asyncio
from passlib.context import CryptContext
from sqlalchemy import text
from src.database.session import engine

# Usamos el estándar exacto de seguridad de tu API
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def sync_password():
    password_plano = "vantec2026"
    hash_nativo = pwd_context.hash(password_plano)
    
    print(f"Generando hash nativo de Vantec: {hash_nativo}")
    
    async with engine.begin() as conn:
        # Actualizamos el usuario con el hash garantizado
        await conn.execute(
            text("UPDATE users SET password_hash = :hash WHERE username = 'eroblesj'"),
            {"hash": hash_nativo}
        )
    print("✅ Sincronización completa. El password es 100% compatible.")

if __name__ == "__main__":
    asyncio.run(sync_password())