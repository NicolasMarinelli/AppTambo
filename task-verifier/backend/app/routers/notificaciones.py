from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_supervisor
from app.schemas.notificacion import NotificacionResponse, NotificacionDetalleResponse
from app.services import notificacion_service

router = APIRouter()


@router.get("", response_model=List[NotificacionResponse])
async def listar_notificaciones(
    solo_no_leidas: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """
    Lista todas las notificaciones del supervisor.
    Usá ?solo_no_leidas=true para filtrar solo las pendientes.
    """
    return notificacion_service.get_notificaciones(db, current_user.id, solo_no_leidas)


@router.get("/count")
async def contar_no_leidas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Cuenta notificaciones no leídas. Útil para el badge del frontend."""
    notifs = notificacion_service.get_notificaciones(db, current_user.id, solo_no_leidas=True)
    return {"no_leidas": len(notifs)}


@router.get("/{notificacion_id}", response_model=NotificacionDetalleResponse)
async def get_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Detalle de una notificación con la foto y resultado de la IA."""
    return notificacion_service.get_detalle_notificacion(db, notificacion_id, current_user.id)


@router.patch("/{notificacion_id}/leer", response_model=NotificacionResponse)
async def marcar_leida(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Marca una notificación como leída."""
    return notificacion_service.marcar_leida(db, notificacion_id, current_user.id)


@router.patch("/leer-todas", response_model=dict)
async def marcar_todas_leidas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Marca todas las notificaciones como leídas."""
    cantidad = notificacion_service.marcar_todas_leidas(db, current_user.id)
    return {"marcadas": cantidad}


@router.post("/verificar-vencidas")
async def verificar_vencidas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """
    Dispara manualmente la verificación de tareas vencidas.
    En producción esto lo haría un job automático (cron).
    """
    creadas = notificacion_service.verificar_tareas_vencidas(db)
    return {"notificaciones_creadas": creadas}