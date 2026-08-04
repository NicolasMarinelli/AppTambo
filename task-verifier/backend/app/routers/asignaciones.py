from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_supervisor
from app.schemas.asignacion import AsignacionCreate, AsignacionResponse, AsignacionDetalleResponse
from app.schemas.user import UserResponse
from app.services import asignacion_service

router = APIRouter()




@router.post("/{checklist_id}/asignaciones", response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED)
async def asignar(
    checklist_id: int,
    data: AsignacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Asigna un checklist a un operario."""
    return asignacion_service.asignar_checklist(db, checklist_id, data.operario_id, current_user.id)


@router.get("/{checklist_id}/asignaciones", response_model=List[AsignacionDetalleResponse])
async def listar_asignaciones(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Lista todos los operarios asignados a un checklist."""
    return asignacion_service.listar_asignaciones(db, checklist_id, current_user.id)


@router.delete("/{checklist_id}/asignaciones/{operario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desasignar(
    checklist_id: int,
    operario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Elimina la asignación de un operario a un checklist."""
    asignacion_service.desasignar_checklist(db, checklist_id, operario_id, current_user.id)