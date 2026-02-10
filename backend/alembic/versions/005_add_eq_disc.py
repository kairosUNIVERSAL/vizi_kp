"""add equipment and discounts

Revision ID: 005_add_eq_disc
Revises: 004_company_profile
Create Date: 2026-02-10 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_add_eq_disc'
down_revision: Union[str, None] = '004_company_profile'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Categories
    op.add_column('categories', sa.Column('is_equipment', sa.Boolean(), server_default='false', nullable=True))
    
    # Price Items
    op.add_column('price_items', sa.Column('synonyms', sa.Text(), server_default='', nullable=True))
    
    # Estimates
    op.add_column('estimates', sa.Column('discount_pr_work', sa.Numeric(precision=5, scale=2), server_default='0', nullable=True))
    op.add_column('estimates', sa.Column('discount_equipment', sa.Numeric(precision=5, scale=2), server_default='0', nullable=True))


def downgrade() -> None:
    # Estimates
    op.drop_column('estimates', 'discount_equipment')
    op.drop_column('estimates', 'discount_pr_work')
    
    # Price Items
    op.drop_column('price_items', 'synonyms')
    
    # Categories
    op.drop_column('categories', 'is_equipment')
