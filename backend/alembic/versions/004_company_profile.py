"""Add company profile and user stats fields

Revision ID: 004_company_profile
Revises: 003_price_items
Create Date: 2026-02-05
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_company_profile'
down_revision: Union[str, None] = '003_price_items'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Company profile fields
    op.add_column('companies', sa.Column('logo_path', sa.String(500), nullable=True))
    op.add_column('companies', sa.Column('address', sa.String(500), server_default='', nullable=False))
    op.add_column('companies', sa.Column('website', sa.String(255), server_default='', nullable=False))
    op.add_column('companies', sa.Column('messenger_contact', sa.String(100), server_default='', nullable=False))
    op.add_column('companies', sa.Column('messenger_type', sa.String(20), server_default='telegram', nullable=False))
    
    # Payment details
    op.add_column('companies', sa.Column('inn', sa.String(12), server_default='', nullable=False))
    op.add_column('companies', sa.Column('kpp', sa.String(9), server_default='', nullable=False))
    op.add_column('companies', sa.Column('bank_name', sa.String(255), server_default='', nullable=False))
    op.add_column('companies', sa.Column('bank_account', sa.String(20), server_default='', nullable=False))
    op.add_column('companies', sa.Column('bank_bik', sa.String(9), server_default='', nullable=False))
    op.add_column('companies', sa.Column('bank_corr', sa.String(20), server_default='', nullable=False))
    
    # User statistics
    op.add_column('users', sa.Column('total_tokens_used', sa.Integer, server_default='0', nullable=False))
    op.add_column('users', sa.Column('total_api_cost', sa.Numeric(10, 4), server_default='0', nullable=False))


def downgrade() -> None:
    # User statistics
    op.drop_column('users', 'total_api_cost')
    op.drop_column('users', 'total_tokens_used')
    
    # Payment details
    op.drop_column('companies', 'bank_corr')
    op.drop_column('companies', 'bank_bik')
    op.drop_column('companies', 'bank_account')
    op.drop_column('companies', 'bank_name')
    op.drop_column('companies', 'kpp')
    op.drop_column('companies', 'inn')
    
    # Company profile fields
    op.drop_column('companies', 'messenger_type')
    op.drop_column('companies', 'messenger_contact')
    op.drop_column('companies', 'website')
    op.drop_column('companies', 'address')
    op.drop_column('companies', 'logo_path')
