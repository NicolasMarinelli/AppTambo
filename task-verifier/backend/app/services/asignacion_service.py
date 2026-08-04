from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.checklist import ChecklistAsignacion
from app.models.user import User, RolUsuario
from app.services.checklist_service import get_checklist_or_404


def asignar_checklist(db: Session, checklist_id: int, operario_id: int, supervisor_id: int) -> ChecklistAsignacion:
    """Asigna un checklist a un operario."""

    # Verificar que el checklist existe y pertenece al supervisor
    checklist = get_checklist_or_404(db, checklist_id)
    if checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para asignar este checklist",
        )

    # Verificar que el operario existe y tiene rol correcto
    operario = db.query(User).filter(User.id == operario_id).first()
    if not operario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operario no encontrado",
        )
    if operario.rol != RolUsuario.operario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario seleccionado no es un operario",
        )

    # Verificar que no esté ya asignado
    existente = db.query(ChecklistAsignacion).filter(
        ChecklistAsignacion.checklist_id == checklist_id,
        ChecklistAsignacion.operario_id == operario_id,
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este checklist ya está asignado a ese operario",
        )

    asignacion = ChecklistAsignacion(
        checklist_id=checklist_id,
        operario_id=operario_id,
    )
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


def desasignar_checklist(db: Session, checklist_id: int, operario_id: int, supervisor_id: int) -> None:
    """Elimina la asignación de un checklist a un operario."""

    checklist = get_checklist_or_404(db, checklist_id)
    if checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para modificar este checklist",
        )

    asignacion = db.query(ChecklistAsignacion).filter(
        ChecklistAsignacion.checklist_id == checklist_id,
        ChecklistAsignacion.operario_id == operario_id,
    ).first()
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe esa asignación",
        )

    db.delete(asignacion)
    db.commit()


def listar_asignaciones(db: Session, checklist_id: int, supervisor_id: int, ) -> list[ChecklistAsignacion]:
    """Lista todos los operarios asignados a un checklist."""

    checklist = get_checklist_or_404(db, checklist_id)
    if checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para ver este checklist",
        )

    return db.query(ChecklistAsignacion).filter(
        ChecklistAsignacion.checklist_id == checklist_id,
    ).all()


def listar_operarios(db: Session,empresa_id= int ) -> list[User]:
    """Lista todos los operarios disponibles para asignar."""
    return db.query(User).filter(User.rol == RolUsuario.operario and User.empresa_id == empresa_id).all()