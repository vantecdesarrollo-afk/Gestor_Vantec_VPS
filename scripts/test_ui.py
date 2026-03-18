import asyncio
import httpx
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.session import AsyncSessionLocal
from src.database.models import Usuario
from sqlalchemy import select
from src.api.endpoints.auth import create_access_token

async def main():
    print("Iniciando validación de Back-End (Fix de Dependencias - 401)")
    
    # 1. Generar token
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario))
        user = result.scalars().first()
        if not user:
            print("No users found to test with.")
            return

        print(f"Testing Auth Fallback with User ID: {user.id}")
        token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "is_superadmin": user.is_superadmin,
                "entidades": [],
                "username": user.username
            }
        )

    # 2. Probar API Endpoint usando GET param ?token=
    print(f"\n[Test] Evaluando endpoint protegido con ?token=")
    async with httpx.AsyncClient() as client:
        # Usamos /api/v1/auth/login?token= ... esperemos, auth/login no está protegido, 
        # mejor /api/v1/admin/usuarios
        url = f"http://localhost:8002/api/v1/admin/usuarios?token={token}"
        print(f"GET {url}")
        res = await client.get(url)
        print(f"Status Result: {res.status_code}")
        
        if res.status_code == 200:
            print("🚀 ÉXITO: El endpoint aceptó el token por URL. El Error 401 de Unauthorized para descargas PDF (cadena de dependencia) fue arreglado exitosamente.")
        else:
            print(f"🛑 FALLA: {res.status_code} - {res.text}")

if __name__ == "__main__":
    asyncio.run(main())
