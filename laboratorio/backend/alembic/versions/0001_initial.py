"""initial schema for laboratorio (schema-scoped, nunca toca public.users)

Revision ID: 0001
Revises:
Create Date: 2026-08-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

etiqueta_foto = sa.Enum("aprobado", "rechazado", name="etiqueta_foto", schema="laboratorio")
veredicto_ia = sa.Enum("aprobado", "no_aprobado", name="veredicto_ia", schema="laboratorio")
estado_resultado = sa.Enum("pendiente", "aprobado", "rechazado", name="estado_resultado", schema="laboratorio")


def upgrade() -> None:
    # El schema "laboratorio" NO se crea acá — infra/postgres-init/init-multiple-dbs.sh
    # ya lo hace (con AUTHORIZATION del rol de laboratorio) al levantar el
    # volumen por primera vez, corriendo como superusuario. No se puede
    # hacer también desde acá "por las dudas": en Postgres 15+ solo el
    # dueño de la base (o un superusuario) tiene privilegio CREATE sobre
    # ella por defecto, y el rol de laboratorio corre esta migración sin
    # ese privilegio a propósito (ver infra/postgres-init) — un
    # CREATE SCHEMA IF NOT EXISTS acá falla con "permission denied" aunque
    # el schema ya exista, porque el chequeo de permiso es previo al de
    # existencia. Si este entorno no corrió ese script (ej. un volumen
    # viejo de antes de que laboratorio existiera), hay que crear el
    # schema a mano una vez — ver laboratorio/backend/README.md.
    op.create_table(
        "tipos_analisis",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("criterios_ia", sa.Text(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
        schema="laboratorio",
    )
    op.create_index("ix_laboratorio_tipos_analisis_slug", "tipos_analisis", ["slug"], schema="laboratorio")

    op.create_table(
        "fotos_referencia",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "tipo_analisis_id",
            sa.Integer(),
            sa.ForeignKey("laboratorio.tipos_analisis.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("imagen_url", sa.String(500), nullable=False),
        sa.Column("etiqueta", etiqueta_foto, nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("subido_por", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="laboratorio",
    )
    op.create_index(
        "ix_laboratorio_fotos_referencia_tipo_analisis_id",
        "fotos_referencia",
        ["tipo_analisis_id"],
        schema="laboratorio",
    )

    op.create_table(
        "resultados_laboratorio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "tipo_analisis_id",
            sa.Integer(),
            sa.ForeignKey("laboratorio.tipos_analisis.id"),
            nullable=False,
        ),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("identificacion_muestra", sa.String(200), nullable=False),
        sa.Column("foto_muestra_url", sa.String(500), nullable=False),
        sa.Column("ufc", sa.String(50), nullable=True),
        sa.Column("veredicto_ia", veredicto_ia, nullable=False),
        sa.Column("confianza_ia", sa.Numeric(3, 2), nullable=False),
        sa.Column("justificacion_ia", sa.Text(), nullable=False),
        sa.Column("veredicto_final", veredicto_ia, nullable=True),
        sa.Column("revisado_por", sa.Integer(), nullable=True),
        sa.Column("revisado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estado", estado_resultado, nullable=False, server_default="pendiente"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="laboratorio",
    )
    op.create_index(
        "ix_laboratorio_resultados_usuario_id", "resultados_laboratorio", ["usuario_id"], schema="laboratorio"
    )
    op.create_index(
        "ix_laboratorio_resultados_tipo_analisis_id",
        "resultados_laboratorio",
        ["tipo_analisis_id"],
        schema="laboratorio",
    )


def downgrade() -> None:
    op.drop_table("resultados_laboratorio", schema="laboratorio")
    op.drop_table("fotos_referencia", schema="laboratorio")
    op.drop_table("tipos_analisis", schema="laboratorio")

    bind = op.get_bind()
    estado_resultado.drop(bind, checkfirst=True)
    veredicto_ia.drop(bind, checkfirst=True)
    etiqueta_foto.drop(bind, checkfirst=True)
