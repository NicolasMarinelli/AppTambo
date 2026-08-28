from datetime import datetime

from pydantic import BaseModel, Field


class TipoAnalisisBase(BaseModel):
    nombre: str = Field(..., max_length=120)
    slug: str = Field(..., max_length=120, description="Identificador corto y estable, ej. 'mastitis'")
    descripcion: str | None = None
    criterios_ia: str = Field(..., description="Instrucciones para la IA sobre qué mirar en la foto")
    activo: bool = True


class TipoAnalisisCreate(TipoAnalisisBase):
    pass


class TipoAnalisisUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    criterios_ia: str | None = None
    activo: bool | None = None


class TipoAnalisisOut(TipoAnalisisBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
