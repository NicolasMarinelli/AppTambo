from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_lab_or_admin
from app.core.database import get_db
from app.models.enums import EtiquetaFoto
from app.models.foto_referencia import FotoReferencia
from app.models.tipo_analisis import TipoAnalisis
from app.models.user import User
from app.schemas.foto_referencia import FotoReferenciaOut
from app.services.storage import save_photo

router = APIRouter(prefix="/tipos-analisis/{tipo_id}/fotos-referencia", tags=["fotos-referencia"])


@router.get("", response_model=list[FotoReferenciaOut], dependencies=[Depends(get_current_user)])
def list_fotos(tipo_id: int, incluir_inactivas: bool = False, db: Session = Depends(get_db)):
    query = db.query(FotoReferencia).filter(FotoReferencia.tipo_analisis_id == tipo_id)
    if not incluir_inactivas:
        query = query.filter(FotoReferencia.activo.is_(True))
    return query.order_by(FotoReferencia.created_at.desc()).all()


@router.post(
    "",
    response_model=FotoReferenciaOut,
    status_code=status.HTTP_201_CREATED,
    description="Sube una foto modelo (aprobado/rechazado) de referencia para este tipo de análisis.",
)
async def create_foto(
    tipo_id: int,
    etiqueta: EtiquetaFoto = Form(...),
    descripcion: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_lab_or_admin),
):
    tipo = db.get(TipoAnalisis, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de análisis no encontrado")

    url = await save_photo(file, subfolder=f"referencia/{tipo.slug}")

    foto = FotoReferencia(
        tipo_analisis_id=tipo_id,
        imagen_url=url,
        etiqueta=etiqueta,
        descripcion=descripcion,
        subido_por=current_user.id,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


@router.delete(
    "/{foto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Desactiva (soft-delete) una foto de referencia — deja de usarse en futuros análisis.",
)
def deactivate_foto(
    tipo_id: int,
    foto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_lab_or_admin),
):
    foto = (
        db.query(FotoReferencia)
        .filter(FotoReferencia.id == foto_id, FotoReferencia.tipo_analisis_id == tipo_id)
        .first()
    )
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto no encontrada")

    foto.activo = False
    db.commit()
