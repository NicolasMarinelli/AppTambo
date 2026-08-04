"""agregar es_principal manual

Revision ID: e5e52aab256f
Revises: a33a8ffdc98b
Create Date: 2026-04-10 11:48:10.039341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5e52aab256f'
down_revision: Union[str, None] = 'a33a8ffdc98b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',
        sa.Column('es_principal', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    op.drop_column('users', 'es_principal')