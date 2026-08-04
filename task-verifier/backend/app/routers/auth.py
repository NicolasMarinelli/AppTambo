from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.empresa import Empresa, CodigoInvitacion, PlanEmpresa
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.dependencies import get_current_user
from app.services.empresa_service import (
    crear_empresa, validar_y_usar_codigo, generar_codigo_invitacion, get_info_empresa
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class RegisterRequest(BaseModel):
    nombre: str
    email: str
    password: str
    nombre_empresa: Optional[str] = None
    plan: Optional[PlanEmpresa] = None
    codigo_invitacion: Optional[str] = None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registro con dos flujos:
    - Supervisor nuevo: nombre_empresa + plan (crea la empresa)
    - Operario o supervisor adicional: codigo_invitacion
    """
    # Verificar email único
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, detail="Ya existe un usuario con ese email")

    empresa_id = None
    rol = None
    es_principal= False

    if data.codigo_invitacion:
        # Flujo con código — operarios y supervisores adicionales
        codigo = validar_y_usar_codigo(db, data.codigo_invitacion)
        empresa_id = codigo.empresa_id
        rol = codigo.rol_destino
        codigo.usado = True
        db.commit()

    elif data.nombre_empresa and data.plan:
        # Flujo nuevo cliente — crea empresa y se convierte en supervisor
        empresa = crear_empresa(
            db=db,
            nombre=data.nombre_empresa,
            email_contacto=data.email,
            plan=data.plan,
        )
        empresa_id = empresa.id
        rol = "supervisor"
        es_principal = True

    else:
        raise HTTPException(
            400,
            detail="Necesitás un código de invitación o registrarte como nueva empresa",
        )

    from app.models.user import RolUsuario
    new_user = User(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=RolUsuario(rol),
        empresa_id=empresa_id,
        es_principal=es_principal,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(401, detail="Email o contraseña incorrectos")
    
    db.refresh(user)
    # Log temporal para debug
    print(f"DEBUG LOGIN - es_principal: {user.es_principal}, tipo: {type(user.es_principal)}")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/empresa/info")
async def get_empresa_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Info de créditos y membresía — para el widget del supervisor."""
    if not current_user.empresa_id:
        raise HTTPException(404, detail="Usuario sin empresa asignada")
    return get_info_empresa(db, current_user.empresa_id)


@router.get("/empresa/codigos")
async def listar_codigos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los códigos generados por esta empresa."""
    if not current_user.es_principal:
        raise HTTPException(403, detail="Solo el supervisor principal puede ver los códigos")

    codigos = db.query(CodigoInvitacion).filter(
        CodigoInvitacion.empresa_id == current_user.empresa_id,
    ).order_by(CodigoInvitacion.creado_en.desc()).all()

    return [
        {
            "id": c.id,
            "codigo": c.codigo,
            "rol_destino": c.rol_destino,
            "usado": c.usado,
            "creado_en": c.creado_en,
        }
        for c in codigos
    ]


@router.post("/empresa/codigos")
async def crear_codigo(
    rol_destino: str = "operario",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """El supervisor genera códigos para invitar a su equipo."""
    from app.models.user import RolUsuario
    if current_user.rol != RolUsuario.supervisor:
        raise HTTPException(403, detail="Solo supervisores pueden generar códigos")
    if not current_user.empresa_id:
        raise HTTPException(400, detail="Sin empresa asignada")
    if rol_destino not in ["supervisor", "operario"]:
        raise HTTPException(400, detail="Rol inválido")
    codigo = generar_codigo_invitacion(db, current_user.empresa_id, rol_destino)
    return {"codigo": codigo.codigo, "rol_destino": codigo.rol_destino}