from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_supervisor
from app.schemas.user import UserResponse
from app.services.asignacion_service import listar_operarios

router = APIRouter()


@router.get("/operarios", response_model=List[UserResponse])
async def get_operarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_supervisor),
):
    """Lista todos los operarios disponibles para asignar."""
    return listar_operarios(db)