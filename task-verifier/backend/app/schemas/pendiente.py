from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.checklist import ChecklistItemResponse
from app.models.checklist import FrecuenciaChecklist


class ItemPendienteResponse(BaseModel):
    """Item con info de si ya fue respondido en el período actual"""
    id: int
    pregunta: str
    descripcion: Optional[str] = None
    foto_referencia_url: Optional[str] = None
    orden: int
    ya_respondido: bool = False
    permite_foto: bool = False

    model_config = {"from_attributes": True}


class ChecklistPendienteResponse(BaseModel):
    """Checklist con el progreso del operario en el período actual"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    frecuencia: FrecuenciaChecklist
    items: List[ItemPendienteResponse]
    total_items: int
    items_completados: int
    completado: bool
    

    model_config = {"from_attributes": True}