"""initial schema + seed data

Revision ID: 0001
Revises:
Create Date: 2026-07-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.security import hash_password
from app.core.config import settings

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Each enum type below is used by exactly one table, so create_table's own
# implicit "create if not exists" is the sole place the Postgres ENUM type
# gets created - no separate pre-create step needed (and generic sa.Enum
# doesn't honor a create_type=False override, so don't try that here).
user_role = sa.Enum("admin", "operario", "laboratorio", name="user_role")
sequence_name = sa.Enum("caravana_macho", "caravana_hembra", "senasa", name="sequence_name")
tipo_cria = sa.Enum("macho_vivo", "macho_muerto", "hembra_viva", "hembra_muerta", name="tipo_cria")
calostro_tipo = sa.Enum("natural", "mejorado", "preparado", name="calostro_tipo")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "animals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("caravana", sa.String(50), nullable=False),
        sa.Column("sexo", sa.String(10), nullable=False),
        sa.Column("estado", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("caravana"),
    )
    op.create_index("ix_animals_caravana", "animals", ["caravana"])

    op.create_table(
        "sequence_counters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sequence_name, nullable=False),
        sa.Column("ultimo_valor", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("nombre"),
    )

    op.create_table(
        "calf_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=False),
        sa.Column("hora_parto", sa.Time(), nullable=False),
        sa.Column("madre_caravana", sa.String(50), nullable=True),
        sa.Column("parto_asistido", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("mellizo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("peso_nacimiento_kg", sa.Numeric(5, 2), nullable=False),
        sa.Column("tipo_cria", tipo_cria, nullable=False),
        sa.Column("caravana_asignada", sa.Integer(), nullable=True),
        sa.Column("numero_senasa", sa.Integer(), nullable=True),
        sa.Column("calostro_tipo", calostro_tipo, nullable=False),
        sa.Column("calostro_brix", sa.Numeric(4, 2), nullable=False),
        sa.Column("calostro_cantidad_litros", sa.Numeric(5, 2), nullable=False),
        sa.Column("calostro_bolsa_numero", sa.String(50), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_calf_records_madre_caravana", "calf_records", ["madre_caravana"])
    op.create_index("ix_calf_records_calostro_bolsa_numero", "calf_records", ["calostro_bolsa_numero"])

    op.create_table(
        "calf_records_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("calf_record_id", sa.Integer(), sa.ForeignKey("calf_records.id"), nullable=False),
        sa.Column("previous_state", sa.JSON(), nullable=False),
        sa.Column("edited_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("edited_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_calf_records_audit_calf_record_id", "calf_records_audit", ["calf_record_id"])

    # Seed default sequence counters
    op.bulk_insert(
        sa.table(
            "sequence_counters",
            sa.column("nombre", sequence_name),
            sa.column("ultimo_valor", sa.Integer()),
        ),
        [
            {"nombre": "caravana_macho", "ultimo_valor": 0},
            {"nombre": "caravana_hembra", "ultimo_valor": 0},
            {"nombre": "senasa", "ultimo_valor": 0},
        ],
    )

    # Seed default admin user (password must be changed on first login)
    op.bulk_insert(
        sa.table(
            "users",
            sa.column("username", sa.String),
            sa.column("password_hash", sa.String),
            sa.column("role", user_role),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "username": settings.default_admin_username,
                "password_hash": hash_password(settings.default_admin_password),
                "role": "admin",
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("calf_records_audit")
    op.drop_table("calf_records")
    op.drop_table("sequence_counters")
    op.drop_table("animals")
    op.drop_table("users")

    bind = op.get_bind()
    calostro_tipo.drop(bind, checkfirst=True)
    tipo_cria.drop(bind, checkfirst=True)
    sequence_name.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
