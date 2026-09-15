"""generated reports

Revision ID: 50e44a835cae
Revises: 0d195a01051b
Create Date: 2026-09-16

"""
import sqlalchemy as sa
from alembic import op

revision = "50e44a835cae"
down_revision = "0d195a01051b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "generated_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filing_period_id", sa.Integer(), sa.ForeignKey("filing_periods.id"), nullable=False),
        sa.Column("report_type", sa.String(32), nullable=False),
        sa.Column("sections_json", sa.Text(), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_generated_reports_period_type", "generated_reports", ["filing_period_id", "report_type"])


def downgrade() -> None:
    op.drop_table("generated_reports")
