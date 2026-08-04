from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.checklist import ChecklistListResponse


class AsignacionCreate(BaseModel):
    operario_id: int


class AsignacionResponse(BaseModel):
    id: int
    checklist_id: int
    operario_id: int
    asignado_en: datetime

    model_config = {"from_attributes": True}


class AsignacionDetalleResponse(BaseModel):
    id: int
    checklist_id: int
    asignado_en: datetime
    operario: UserResponse

    model_config = {"from_attributes": True}