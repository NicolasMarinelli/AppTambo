from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.notificacion import TipoNotificacion


class NotificacionResponse(BaseModel):
    id: int
    supervisor_id: int
    respuesta_id: Optional[int] = None
    tipo: TipoNotificacion
    mensaje: str
    leida: bool
    fecha: datetime

    model_config = {"from_attributes": True}


class NotificacionDetalleResponse(NotificacionResponse):
    """Con info de la respuesta asociada si existe"""
    foto_url: Optional[str] = None
    resultado_ia: Optional[dict] = None
    operario_nombre: Optional[str] = None
    pregunta: Optional[str] = None