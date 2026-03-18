import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Seguridad y JWT
    SECRET_KEY: str = os.getenv("VANTEC_SECRET_KEY", "VANTEC_SECRET_KEY_CHANGEME")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 2
    
    # Base de Datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://vantec_user:vantec_password@localhost/gestor_cfdi"
    )
    
    # Almacenamiento
    STORAGE_PATH: str = "/storage"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
