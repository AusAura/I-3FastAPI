"""empty message

Revision ID: 1e62ef5558ab
Revises: a6a95392be5d
Create Date: 2024-01-13 11:39:32.787582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e62ef5558ab'
down_revision: Union[str, None] = 'a6a95392be5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
