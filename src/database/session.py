from fastapi import Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from src.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db(request: Request):
    """
    Generador de sesión de BD. Inyecta el tenant_id en PostgreSQL
    para activar el Row Level Security (RLS) de Vantec.
    """
    async with AsyncSessionLocal() as session:
        # Extraemos el tenant_id que el middleware guardó en request.state
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if tenant_id:
            # ¡EL BLINDAJE DE SEGURIDAD CORREGIDO!
            # PostgreSQL no permite bind parameters en comandos SET.
            # Usamos set_config para inyectar el tenant_id de forma segura.
            await session.execute(
                text("SELECT set_config('app.current_tenant_id', :tid, true)"),
                {"tid": str(tenant_id)}
            )
            
        yield session
