"""Stub for missing 003

Revision ID: 003_price_items
Revises: None
Create Date: 2026-02-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_price_items'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
