"""Shadow read-only de la tabla `users` de tambo.

laboratorio no tiene usuarios propios: se conecta a la misma base de datos
que tambo ("cami") con un rol de Postgres que solo tiene SELECT sobre
`public.users` (ver infra/postgres-init/init-multiple-dbs.sh en la raíz del
repo). Esta clase mapea esa tabla tal cual la define
tambo/backend/app/models/user.py.

No se migra desde acá — alembic/env.py excluye explícitamente el schema
"public" de las migraciones de laboratorio — y no debería hacerse nunca un
INSERT/UPDATE/DELETE contra esta tabla desde este servicio (la gestión de
usuarios sigue siendo 100% de tambo).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # create_type=False: el tipo Postgres "user_role" ya existe (lo crea la
    # migración de tambo) — nunca hay que intentar recrearlo desde acá.
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", create_type=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
