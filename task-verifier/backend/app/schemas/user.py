from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import RolUsuario


class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: RolUsuario

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: RolUsuario
    empresa_id: Optional[int] = None
    es_principal: bool = False   
    creado_en: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse