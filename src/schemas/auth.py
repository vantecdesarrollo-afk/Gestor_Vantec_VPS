from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

# Router 100% limpio, sin prefijos que se enreden
router = APIRouter(tags=["Autenticación"])

# RUTA ABSOLUTA: Aquí definimos exactamente lo que Swagger va a buscar
@router.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"\n[+] Vantec Auth System -> Intento de: {form_data.username}")
    
    if form_data.username != "eroblesj":
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado en la fábrica de software Vantec",
        )

    return {"access_token": "token_pro_vantec", "token_type": "bearer"}