from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import ALLOWED_ROLES, get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    description=(
        "Login con el mismo usuario y contraseña que tambo. Solo entran "
        "admin y laboratorio — cualquier otro rol válido recibe 403 "
        "'Acceso denegado' aunque la contraseña sea correcta."
    ),
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    # Mismo secreto/algoritmo/forma de payload que tambo (sub + role + exp):
    # un token emitido acá es válido en tambo, y uno emitido en tambo es
    # válido acá, sin tener que loguearse dos veces.
    token = create_access_token(subject=user.username, role=user.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut, description="Datos del usuario autenticado")
def me(current_user: User = Depends(get_current_user)):
    return current_user
