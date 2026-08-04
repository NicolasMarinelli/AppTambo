from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from app.utils.storage import save_photo
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_supervisor
from app.schemas.checklist import (
    ChecklistCreate, ChecklistUpdate, ChecklistResponse, ChecklistListResponse,
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse,
)
from app.services import checklist_service
from app.services.respuesta_service import get_todas_respuestas_supervisor
from app.schemas.respuesta import RespuestaResponse


router = APIRouter()


# ── Checklists ────────────────────────────────────────────────────

@router.post("", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    data: ChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Crea un checklist con sus items. Solo supervisores."""
    return checklist_service.create_checklist(db, data, current_user.id)


@router.get("", response_model=List[ChecklistListResponse])
async def list_checklists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Lista todos los checklists del supervisor autenticado."""
    checklists = checklist_service.list_checklists(db, current_user.id)
    result = []
    for c in checklists:
        result.append(ChecklistListResponse(
            id=c.id,
            nombre=c.nombre,
            descripcion=c.descripcion,
            frecuencia=c.frecuencia,
            creado_por=c.creado_por,
            creado_en=c.creado_en,
            total_items=len(c.items),
        ))
    return result


@router.get("/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Obtiene un checklist con todos sus items."""
    return checklist_service.get_checklist_or_404(db, checklist_id)


@router.patch("/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    checklist_id: int,
    data: ChecklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Actualiza nombre, descripcion o frecuencia."""
    return checklist_service.update_checklist(db, checklist_id, data, current_user.id)


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Elimina el checklist y todos sus items."""
    checklist_service.delete_checklist(db, checklist_id, current_user.id)


# ── Items ─────────────────────────────────────────────────────────

@router.post("/{checklist_id}/items", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    checklist_id: int,
    data: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Agrega un item a un checklist existente."""
    return checklist_service.add_item(db, checklist_id, data, current_user.id)


@router.patch("/items/{item_id}", response_model=ChecklistItemResponse)
async def update_item(
    item_id: int,
    data: ChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Edita pregunta, descripcion u orden de un item."""
    return checklist_service.update_item(db, item_id, data, current_user.id)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Elimina un item del checklist."""
    checklist_service.delete_item(db, item_id, current_user.id)


@router.get("/respuestas/todas", response_model=List[RespuestaResponse])
async def ver_todas_respuestas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """
    Panel del supervisor: ve todas las respuestas de sus checklists.
    Ordenadas por fecha descendente.
    """
    return get_todas_respuestas_supervisor(db, current_user.id)



from app.services.respuesta_service import (
    get_todas_respuestas_supervisor,
    get_respuesta_detalle,
    dar_feedback,
    get_estadisticas_ia,
)

from app.schemas.respuesta import RespuestaResponse, RespuestaDetalleResponse, FeedbackSupervisor


@router.get("/respuestas/todas", response_model=List[RespuestaResponse])
async def ver_todas_respuestas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Panel del supervisor: todas las respuestas de sus checklists."""
    return get_todas_respuestas_supervisor(db, current_user.id)


@router.get("/respuestas/estadisticas-ia")
async def estadisticas_ia(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """
    Métricas de precisión de la IA.
    Muestra cuántas veces acertó vs cuántas el supervisor la corrigió.
    """
    return get_estadisticas_ia(db, current_user.id)


@router.get("/respuestas/{respuesta_id}", response_model=RespuestaDetalleResponse)
async def ver_respuesta(
    respuesta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Detalle de una respuesta: foto, resultado IA, info del operario."""
    return get_respuesta_detalle(db, respuesta_id, current_user.id)


@router.patch("/respuestas/{respuesta_id}/feedback", response_model=RespuestaResponse)
async def feedback_respuesta(
    respuesta_id: int,
    feedback: FeedbackSupervisor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """
    El supervisor da su veredicto final sobre una respuesta.
    Confirma o corrige la decisión de la IA.
    """
    return dar_feedback(
        db=db,
        respuesta_id=respuesta_id,
        supervisor_id=current_user.id,
        aprobado=feedback.aprobado,
        comentario=feedback.comentario,
    )

@router.post("/items/{item_id}/foto-referencia", response_model=ChecklistItemResponse)
async def subir_foto_referencia(
    item_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """
    Sube o reemplaza la foto de referencia de un ítem.
    Si ya tenía una foto, la nueva la sobreescribe.
    """
    item = checklist_service.get_item_or_404(db, item_id)

    # Verificar que el supervisor es dueño del checklist
    if item.checklist.creado_por != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para modificar este ítem",
        )

    # Validar que sea imagen
    if not foto.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, webp)",
        )

    # Guardar foto y actualizar el ítem
    foto_url = await save_photo(foto, subfolder="referencias")
    item.foto_referencia_url = foto_url
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}/foto-referencia", response_model=ChecklistItemResponse)
async def eliminar_foto_referencia(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Elimina la foto de referencia de un ítem."""
    item = checklist_service.get_item_or_404(db, item_id)

    if item.checklist.creado_por != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para modificar este ítem",
        )

    item.foto_referencia_url = None
    db.commit()
    db.refresh(item)
    return item