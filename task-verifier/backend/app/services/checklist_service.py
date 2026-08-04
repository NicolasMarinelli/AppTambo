from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.checklist import Checklist, ChecklistItem
from app.schemas.checklist import ChecklistCreate, ChecklistUpdate, ChecklistItemCreate, ChecklistItemUpdate


def get_checklist_or_404(db: Session, checklist_id: int) -> Checklist:
    """Busca un checklist por ID o lanza 404."""
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checklist {checklist_id} no encontrado",
        )
    return checklist


def get_item_or_404(db: Session, item_id: int) -> ChecklistItem:
    """Busca un item por ID o lanza 404."""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} no encontrado",
        )
    return item


def create_checklist(db: Session, data: ChecklistCreate, supervisor_id: int) -> Checklist:
    """Crea un checklist con sus items en una sola transacción."""
    checklist = Checklist(
        nombre=data.nombre,
        descripcion=data.descripcion,
        frecuencia=data.frecuencia,
        creado_por=supervisor_id,
    )
    db.add(checklist)
    db.flush()  # Obtiene el ID sin hacer commit todavía

    # Crear los items asociados
    for item_data in data.items:
        item = ChecklistItem(
            checklist_id=checklist.id,
            pregunta=item_data.pregunta,
            descripcion=item_data.descripcion,
            foto_referencia_url=item_data.foto_referencia_url,
            orden=item_data.orden,
        )
        db.add(item)

    db.commit()
    db.refresh(checklist)
    return checklist


def list_checklists(db: Session, supervisor_id: int) -> list[Checklist]:
    """Lista todos los checklists creados por este supervisor."""
    return (
        db.query(Checklist)
        .filter(Checklist.creado_por == supervisor_id)
        .order_by(Checklist.creado_en.desc())
        .all()
    )


def update_checklist(db: Session, checklist_id: int, data: ChecklistUpdate, supervisor_id: int) -> Checklist:
    """Actualiza campos del checklist. Solo el creador puede editarlo."""
    checklist = get_checklist_or_404(db, checklist_id)

    if checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para editar este checklist",
        )

    # Actualiza solo los campos que vienen en el request
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(checklist, field, value)

    db.commit()
    db.refresh(checklist)
    return checklist


def delete_checklist(db: Session, checklist_id: int, supervisor_id: int) -> None:
    """Elimina checklist y sus items (cascade). Solo el creador puede eliminarlo."""
    checklist = get_checklist_or_404(db, checklist_id)

    if checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para eliminar este checklist",
        )

    db.delete(checklist)
    db.commit()


# ── Items ─────────────────────────────────────────────────────────

def add_item(db: Session, checklist_id: int, data: ChecklistItemCreate, supervisor_id: int) -> ChecklistItem:
    """Agrega un item a un checklist existente."""
    checklist = get_checklist_or_404(db, checklist_id)

    if checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para modificar este checklist",
        )

    item = ChecklistItem(
        checklist_id=checklist_id,
        pregunta=data.pregunta,
        descripcion=data.descripcion,
        foto_referencia_url=data.foto_referencia_url,
        orden=data.orden,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item_id: int, data: ChecklistItemUpdate, supervisor_id: int) -> ChecklistItem:
    """Actualiza un item. Verifica que el supervisor sea dueño del checklist."""
    item = get_item_or_404(db, item_id)

    if item.checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para modificar este item",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int, supervisor_id: int) -> None:
    """Elimina un item. Verifica que el supervisor sea dueño del checklist."""
    item = get_item_or_404(db, item_id)

    if item.checklist.creado_por != supervisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para eliminar este item",
        )

    db.delete(item)
    db.commit()