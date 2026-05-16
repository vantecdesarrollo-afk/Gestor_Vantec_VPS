import os
from pathlib import Path
from pydantic_settings import BaseSettings

from urllib.parse import quote_plus

def get_database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        # En Coolify, DATABASE_URL puede contener contraseñas con caracteres especiales sin codificar
        from urllib.parse import urlparse, quote_plus, urlunparse
        parsed = urlparse(url)
        if parsed.password:
            safe_password = quote_plus(parsed.password)
            # Reconstruir netloc con password segura
            netloc = f"{parsed.username}:{safe_password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            parsed = parsed._replace(netloc=netloc)
        
        url_str = urlunparse(parsed)
        if url_str.startswith("postgresql://"):
            url_str = url_str.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url_str.startswith("postgres://"):
            url_str = url_str.replace("postgres://", "postgresql+asyncpg://", 1)
        return url_str

    user = os.getenv("POSTGRES_USER", "vantec_user")
    password = quote_plus(os.getenv("POSTGRES_PASSWORD", "vantec_password"))
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "gestor_cfdi")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

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
