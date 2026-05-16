import os
from pathlib import Path
from pydantic_settings import BaseSettings

from urllib.parse import quote_plus

def get_database_url():
    # En Coolify, si el usuario tiene un DATABASE_URL manual, puede estar apuntando a localhost o estar corrupto.
    # Priorizamos siempre los componentes inyectados por docker-compose.
    host = os.getenv("POSTGRES_HOST")
    if host:
        user = os.getenv("POSTGRES_USER", "vantec_user")
        password = quote_plus(os.getenv("POSTGRES_PASSWORD", "vantec_password"))
        port = os.getenv("POSTGRES_PORT", "5432")
        db_name = os.getenv("POSTGRES_DB", "gestor_cfdi")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url
        
    return "postgresql+asyncpg://vantec_user:vantec_password@db:5432/gestor_cfdi"

class Settings(BaseSettings):
    # Seguridad y JWT
    SECRET_KEY: str = os.getenv("VANTEC_SECRET_KEY", "VANTEC_SECRET_KEY_CHANGEME")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 2
    
    # Base de Datos
    DATABASE_URL: str = get_database_url()
    
    # Almacenamiento
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", r"C:\Test_Antigravity\Gestor_CFDI_Vantec\storage"))
    VANTEC_CFDI_ROOT: Path = Path(os.getenv("VANTEC_CFDI_ROOT", r"C:\Test_Antigravity\Gestor_CFDI_Vantec\storage"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
