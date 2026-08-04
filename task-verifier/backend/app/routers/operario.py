from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional 
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_operario
from app.schemas.pendiente import ChecklistPendienteResponse
from app.schemas.respuesta import RespuestaResponse
from app.services.pendiente_service import get_pendientes
from app.services.respuesta_service import crear_respuesta_ia, get_respuestas_item
from app.services.ia_service import analizar_foto_seguro
from app.utils.storage import save_photo

router = APIRouter()


@router.get("/pendientes", response_model=List[ChecklistPendienteResponse])
async def get_mis_pendientes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operario),
):
    """Retorna todos los checklists asignados con estado del período actual."""
    return get_pendientes(db, current_user.id)


@router.post("/responder", response_model=RespuestaResponse)
async def responder_item(
    item_id: int = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operario),
):
    """
    Endpoint principal: el operario sube una foto para un item.
    1. Guarda la foto
    2. La IA la analiza
    3. Guarda el resultado
    4. Si fue rechazada, notifica al supervisor
    """
    # Validar que sea una imagen
    if not foto.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, webp)",
        )

    # Guardar foto
    foto_url = await save_photo(foto, subfolder="respuestas")

    # Crear respuesta con análisis de IA
    respuesta = crear_respuesta_ia(
        db=db,
        item_id=item_id,
        operario_id=current_user.id,
        foto_url=foto_url,
    )

    return respuesta


@router.get("/respuestas/{item_id}", response_model=List[RespuestaResponse])
async def historial_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operario),
):
    """Historial de respuestas del operario para un item específico."""
    return get_respuestas_item(db, item_id, current_user.id)


@router.post("/test-ia")
async def test_ia(
    pregunta: str = Form(default="¿El área de trabajo está limpia y ordenada?"),
    foto: UploadFile = File(...),
    current_user: User = Depends(get_current_operario),
):
    """Endpoint de prueba para verificar que la IA funciona."""
    foto_url = await save_photo(foto, subfolder="test")
    resultado = analizar_foto_seguro(
        pregunta=pregunta,
        foto_respuesta_url=foto_url,
    )
    return {
        "pregunta": pregunta,
        "foto_url": foto_url,
        "resultado_ia": resultado,
    }

@router.post("/responder-convencional", response_model=RespuestaResponse)
async def responder_item_convencional(
    item_id: int = Form(...),
    texto: str = Form(...),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operario),
):
    """Respuesta para checklist convencional — checkbox + texto + foto opcional."""
    foto_url = None
    if foto and foto.content_type.startswith("image/"):
        foto_url = await save_photo(foto, subfolder="convencional")

    respuesta = crear_respuesta_convencional(
        db=db,
        item_id=item_id,
        operario_id=current_user.id,
        texto=texto,
        foto_url=foto_url,
    )
    return respuesta