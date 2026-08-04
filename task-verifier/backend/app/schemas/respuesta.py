from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ResultadoIA(BaseModel):
    aprobado: bool
    confianza: float
    observacion: str


class RespuestaCreate(BaseModel):
    item_id: int


class RespuestaResponse(BaseModel):
    id: int
    item_id: int
    operario_id: int
    foto_url: str
    resultado_ia: Optional[Any] = None
    aprobado_supervisor: Optional[bool] = None
    comentario_supervisor: Optional[str] = None
    fecha: datetime

    model_config = {"from_attributes": True}


class RespuestaDetalleResponse(RespuestaResponse):
    """Versión extendida con info del item y operario"""
    pregunta: str = ""
    checklist_nombre: str = ""
    operario_nombre: str = ""
    foto_referencia_url: Optional[str] = None


class FeedbackSupervisor(BaseModel):
    """Lo que manda el supervisor al revisar"""
    aprobado: bool
    comentario: Optional[str] = None


class EstadisticasIA(BaseModel):
    """Métricas de precisión de la IA"""
    total_revisadas: int
    ia_correcta: int
    ia_incorrecta: int
    precision: float
    pendientes_revision: int