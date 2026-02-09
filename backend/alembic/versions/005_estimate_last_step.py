"""Add last_step to estimates

Revision ID: 005_estimate_last_step
Revises: 004_company_profile
Create Date: 2026-02-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_estimate_last_step'
down_revision: Union[str, None] = '004_company_profile'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('estimates', sa.Column('last_step', sa.Integer, server_default='1', nullable=False))


def downgrade() -> None:
    op.drop_column('estimates', 'last_step')
