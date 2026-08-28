import enum


class UserRole(str, enum.Enum):
    """Espejo del enum Postgres `user_role`, creado por la migración inicial
    de tambo (tambo/backend/alembic/versions/0001_initial.py). No se crea
    acá — ver app/models/user.py y alembic/env.py, que excluyen el schema
    "public" de las migraciones de laboratorio."""

    admin = "admin"
    operario = "operario"
    laboratorio = "laboratorio"


class EtiquetaFoto(str, enum.Enum):
    aprobado = "aprobado"
    rechazado = "rechazado"


class VeredictoIA(str, enum.Enum):
    aprobado = "aprobado"
    no_aprobado = "no_aprobado"


class EstadoResultado(str, enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"
