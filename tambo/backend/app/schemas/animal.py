from datetime import datetime

from pydantic import BaseModel, Field


class AnimalBase(BaseModel):
    caravana: str = Field(..., description="Número de caravana de la madre, único")
    sexo: str = Field(..., description="Sexo del animal (M/H)")
    estado: bool | None = Field(True, description="Activo/inactivo en el establecimiento")


class AnimalCreate(AnimalBase):
    pass


class AnimalOut(AnimalBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
