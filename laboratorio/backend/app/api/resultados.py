from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_lab_or_admin
from app.core.database import get_db
from app.models.enums import EstadoResultado, VeredictoIA
from app.models.foto_referencia import FotoReferencia
from app.models.resultado import ResultadoLaboratorio
from app.models.tipo_analisis import TipoAnalisis
from app.models.user import User
from app.schemas.resultado import ResultadoOut, RevisionInput
from app.services.ia_service import analizar_muestra
from app.services.storage import save_photo

router = APIRouter(prefix="/resultados", tags=["resultados"])


@router.get("", response_model=list[ResultadoOut], dependencies=[Depends(get_current_user)])
def list_resultados(
    tipo_analisis_id: int | None = None,
    estado: EstadoResultado | None = None,
    mine_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ResultadoLaboratorio)
    if tipo_analisis_id is not None:
        query = query.filter(ResultadoLaboratorio.tipo_analisis_id == tipo_analisis_id)
    if estado is not None:
        query = query.filter(ResultadoLaboratorio.estado == estado)
    if mine_only:
        query = query.filter(ResultadoLaboratorio.usuario_id == current_user.id)
    return query.order_by(ResultadoLaboratorio.created_at.desc()).all()


@router.get("/{resultado_id}", response_model=ResultadoOut, dependencies=[Depends(get_current_user)])
def get_resultado(resultado_id: int, db: Session = Depends(get_db)):
    resultado = db.get(ResultadoLaboratorio, resultado_id)
    if resultado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    return resultado


@router.post(
    "",
    response_model=ResultadoOut,
    status_code=status.HTTP_201_CREATED,
    description=(
        "Carga la foto de una muestra, la manda a la IA junto con las fotos de "
        "referencia activas del tipo de análisis, y guarda el resultado en "
        "estado 'pendiente' hasta que un laboratorista lo revise (ver PATCH "
        "/resultados/{id}/revision)."
    ),
)
async def create_resultado(
    tipo_analisis_id: int = Form(...),
    identificacion_muestra: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_lab_or_admin),
):
    tipo = db.get(TipoAnalisis, tipo_analisis_id)
    if tipo is None or not tipo.activo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de análisis no encontrado o inactivo")

    referencias = (
        db.query(FotoReferencia)
        .filter(FotoReferencia.tipo_analisis_id == tipo_analisis_id, FotoReferencia.activo.is_(True))
        .all()
    )
    if not referencias:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este tipo de análisis todavía no tiene fotos de referencia cargadas",
        )

    foto_muestra_url = await save_photo(file, subfolder=f"muestras/{tipo.slug}")

    try:
        analisis = analizar_muestra(
            criterios=tipo.criterios_ia,
            foto_muestra_url=foto_muestra_url,
            fotos_referencia=[(f.imagen_url, f.etiqueta.value, f.descripcion) for f in referencias],
        )
    except Exception:
        # La foto ya se subió a Cloudinary y queda ahí (no es gratis
        # volver a pedirla), pero no guardamos un resultado con un
        # veredicto inventado: mejor que el laboratorista reintente.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo evaluar la muestra con la IA. Probá de nuevo.",
        )

    resultado = ResultadoLaboratorio(
        tipo_analisis_id=tipo.id,
        usuario_id=current_user.id,
        identificacion_muestra=identificacion_muestra,
        foto_muestra_url=foto_muestra_url,
        ufc=analisis["ufc_estimado"],
        veredicto_ia=VeredictoIA(analisis["veredicto"]),
        confianza_ia=analisis["confianza"],
        justificacion_ia=analisis["justificacion"],
        estado=EstadoResultado.pendiente,
    )
    db.add(resultado)
    db.commit()
    db.refresh(resultado)
    return resultado


@router.patch(
    "/{resultado_id}/revision",
    response_model=ResultadoOut,
    description="El laboratorista confirma o corrige el veredicto de la IA. Deja de estar pendiente.",
)
def revisar_resultado(
    resultado_id: int,
    payload: RevisionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_lab_or_admin),
):
    resultado = db.get(ResultadoLaboratorio, resultado_id)
    if resultado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")

    resultado.veredicto_final = payload.veredicto_final
    resultado.revisado_por = current_user.id
    resultado.revisado_en = datetime.now(timezone.utc)
    resultado.estado = (
        EstadoResultado.aprobado if payload.veredicto_final == VeredictoIA.aprobado else EstadoResultado.rechazado
    )

    db.commit()
    db.refresh(resultado)
    return resultado
