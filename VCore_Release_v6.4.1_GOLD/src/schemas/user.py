from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superadmin: Optional[bool] = None
    rol: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    is_active: bool
    is_superadmin: bool
    rol: Optional[str] = "VISOR"

    class Config:
        from_attributes = True # Estándar Grado Industrial Pydantic V2