from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import decode_access_token
from app.models.user import User, RolUsuario

# Le dice a FastAPI que espere un header "Authorization: Bearer <token>"
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency base: valida el token y retorna el usuario actual.
    Usala en cualquier endpoint que requiera estar logueado.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user


def get_current_supervisor(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency para endpoints solo de supervisores.
    Si el usuario es operario, devuelve 403 Forbidden.
    """
    if current_user.rol != RolUsuario.supervisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los supervisores pueden realizar esta acción",
        )
    return current_user


def get_current_operario(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency para endpoints solo de operarios.
    """
    if current_user.rol != RolUsuario.operario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los operarios pueden realizar esta acción",
        )
    return current_user