"""Add activity logs table

Revision ID: 006_activity_logs
Revises: 005_add_eq_disc, 005_estimate_last_step
Create Date: 2026-02-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "006_activity_logs"
down_revision: Union[str, Sequence[str], None] = ("005_add_eq_disc", "005_estimate_last_step")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("user_email", sa.String(length=255), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=True),
        sa.Column("endpoint", sa.String(length=255), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"], unique=False)
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"], unique=False)
    op.create_index("ix_activity_logs_id", "activity_logs", ["id"], unique=False)
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_activity_logs_user_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_created_at", table_name="activity_logs")
    op.drop_index("ix_activity_logs_action", table_name="activity_logs")
    op.drop_table("activity_logs")
