from datetime import datetime

from pydantic import BaseModel

from app.models.enums import EtiquetaFoto

# No hay FotoReferenciaCreate: el alta se hace vía multipart/form-data
# (UploadFile + Form fields), no con un body JSON — ver app/api/fotos_referencia.py.


class FotoReferenciaOut(BaseModel):
    id: int
    tipo_analisis_id: int
    imagen_url: str
    etiqueta: EtiquetaFoto
    descripcion: str | None
    subido_por: int
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}
