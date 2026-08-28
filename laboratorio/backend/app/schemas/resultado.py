from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import EstadoResultado, VeredictoIA

# No hay ResultadoCreate: el alta se hace vía multipart/form-data
# (UploadFile + Form fields) en app/api/resultados.py.


class ResultadoOut(BaseModel):
    id: int
    tipo_analisis_id: int
    usuario_id: int
    identificacion_muestra: str
    foto_muestra_url: str
    ufc: str | None
    veredicto_ia: VeredictoIA
    confianza_ia: float
    justificacion_ia: str
    veredicto_final: VeredictoIA | None
    revisado_por: int | None
    revisado_en: datetime | None
    estado: EstadoResultado
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RevisionInput(BaseModel):
    veredicto_final: VeredictoIA = Field(..., description="Veredicto confirmado o corregido por el laboratorista")
