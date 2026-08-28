from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_lab_or_admin
from app.core.database import get_db
from app.models.tipo_analisis import TipoAnalisis
from app.schemas.tipo_analisis import TipoAnalisisCreate, TipoAnalisisOut, TipoAnalisisUpdate

router = APIRouter(prefix="/tipos-analisis", tags=["tipos-analisis"])


@router.get(
    "",
    response_model=list[TipoAnalisisOut],
    description="Lista los tipos de análisis. Por defecto solo los activos.",
    dependencies=[Depends(get_current_user)],
)
def list_tipos(incluir_inactivos: bool = False, db: Session = Depends(get_db)):
    query = db.query(TipoAnalisis)
    if not incluir_inactivos:
        query = query.filter(TipoAnalisis.activo.is_(True))
    return query.order_by(TipoAnalisis.nombre).all()


@router.get(
    "/{tipo_id}",
    response_model=TipoAnalisisOut,
    dependencies=[Depends(get_current_user)],
)
def get_tipo(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.get(TipoAnalisis, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de análisis no encontrado")
    return tipo


@router.post(
    "",
    response_model=TipoAnalisisOut,
    status_code=status.HTTP_201_CREATED,
    description="Alta de un tipo de análisis nuevo — sin deploy, queda disponible apenas se crea.",
    dependencies=[Depends(require_lab_or_admin)],
)
def create_tipo(payload: TipoAnalisisCreate, db: Session = Depends(get_db)):
    if db.query(TipoAnalisis).filter(TipoAnalisis.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un tipo de análisis con ese slug")

    tipo = TipoAnalisis(**payload.model_dump())
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


@router.put(
    "/{tipo_id}",
    response_model=TipoAnalisisOut,
    description="Edita nombre/descripción/criterios, o activa/desactiva un tipo de análisis.",
    dependencies=[Depends(require_lab_or_admin)],
)
def update_tipo(tipo_id: int, payload: TipoAnalisisUpdate, db: Session = Depends(get_db)):
    tipo = db.get(TipoAnalisis, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de análisis no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tipo, field, value)

    db.commit()
    db.refresh(tipo)
    return tipo
