from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.checklist import FrecuenciaChecklist, TipoChecklist, ModoIA


# ── Checklist Item ────────────────────────────────────────────────

class ChecklistItemCreate(BaseModel):
    pregunta: str
    descripcion: Optional[str] = None
    orden: int = 0
    # IA
    modo_ia: ModoIA = ModoIA.ninguna
    foto_referencia_url: Optional[str] = None
    prompt_referencia: Optional[str] = None
    # Convencional
    permite_foto: bool = False


class ChecklistItemUpdate(BaseModel):
    pregunta: Optional[str] = None
    descripcion: Optional[str] = None
    orden: Optional[int] = None
    modo_ia: Optional[ModoIA] = None
    foto_referencia_url: Optional[str] = None
    prompt_referencia: Optional[str] = None
    permite_foto: Optional[bool] = None

class ChecklistItemResponse(BaseModel):
    id: int
    checklist_id: int
    pregunta: str
    descripcion: Optional[str] = None
    orden: int
    modo_ia: str = "ninguna"  
    foto_referencia_url: Optional[str] = None
    prompt_referencia: Optional[str] = None
    permite_foto: bool

    model_config = {"from_attributes": True}



# ── Checklist ─────────────────────────────────────────────────────

class ChecklistCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    frecuencia: FrecuenciaChecklist
    tipo: TipoChecklist = TipoChecklist.ia
    items: List[ChecklistItemCreate] = []



class ChecklistUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    frecuencia: Optional[FrecuenciaChecklist] = None
    tipo: Optional[TipoChecklist] = None



class ChecklistResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    frecuencia: FrecuenciaChecklist
    tipo: str = "ia" 
    creado_por: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    items: List[ChecklistItemResponse] = []

    model_config = {"from_attributes": True}


class ChecklistListResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    frecuencia: FrecuenciaChecklist
    tipo: str = "ia"          # ← tiene que estar
    creado_por: int
    creado_en: datetime
    total_items: int = 0

    model_config = {"from_attributes": True}
