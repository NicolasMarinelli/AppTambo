from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.database import Base

# Ojo: solo se importan los modelos PROPIOS de laboratorio (schema
# "laboratorio"). app.models.user (schema "public", tabla de tambo) queda
# deliberadamente afuera — ver también el filtro include_name() más abajo,
# que es la barrera real: aunque algo importara User por accidente en el
# futuro, este env.py nunca generaría ni aplicaría DDL sobre schema "public".
from app.models import FotoReferencia, ResultadoLaboratorio, TipoAnalisis  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

LABORATORIO_SCHEMA = "laboratorio"


def include_name(name, type_, parent_names):
    """Restringe todo lo que alembic pueda proponer o aplicar al schema
    "laboratorio". La tabla `users` (schema "public") es de tambo — este
    servicio nunca debe migrarla ni proponer un DROP para ella solo porque
    no está en el metadata de esta app."""
    if type_ == "schema":
        return name in (None, LABORATORIO_SCHEMA)
    if type_ == "table":
        return parent_names.get("schema_name") == LABORATORIO_SCHEMA
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        version_table_schema=LABORATORIO_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            version_table_schema=LABORATORIO_SCHEMA,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
