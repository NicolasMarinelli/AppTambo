from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    username: str = Field(..., description="Nombre de usuario, único")
    role: UserRole = Field(..., description="Rol del usuario: admin, operario o laboratorio")
    is_active: bool = Field(True, description="Si el usuario puede iniciar sesión")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña en texto plano (se hashea al guardar)")


class UserUpdate(BaseModel):
    role: UserRole | None = Field(None, description="Nuevo rol del usuario")
    is_active: bool | None = Field(None, description="Activar/desactivar el usuario")
    password: str | None = Field(None, min_length=6, description="Nueva contraseña, opcional")


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
