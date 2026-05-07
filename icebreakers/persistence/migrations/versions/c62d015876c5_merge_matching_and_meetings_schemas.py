"""Merge matching and meetings schemas

Revision ID: c62d015876c5
Revises: 06be5889e062, 5585158c1262
Create Date: 2026-05-07 14:46:04.094794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c62d015876c5'
down_revision: Union[str, Sequence[str], None] = ('06be5889e062', '5585158c1262')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
