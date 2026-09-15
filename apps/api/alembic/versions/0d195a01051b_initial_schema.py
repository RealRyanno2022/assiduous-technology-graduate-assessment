"""initial schema

Revision ID: 0d195a01051b
Revises:
Create Date: 2026-09-15

"""
import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "0d195a01051b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("ticker", sa.String(32), nullable=False),
        sa.Column("isin", sa.String(32), nullable=False),
        sa.Column("country", sa.String(64), nullable=False),
        sa.Column("sector", sa.String(128), nullable=False),
    )

    op.create_table(
        "source_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("doc_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("published_date", sa.Date(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "filing_periods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id"), nullable=True),
        sa.Column("period_type", sa.String(8), nullable=False),
        sa.Column("period_label", sa.String(32), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("is_audited", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "financial_line_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filing_period_id", sa.Integer(), sa.ForeignKey("filing_periods.id"), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id"), nullable=True),
        sa.Column("statement", sa.String(32), nullable=False),
        sa.Column("line_item", sa.String(128), nullable=False),
        sa.Column("value_eur", sa.Numeric(14, 2), nullable=False),
        sa.Column("comparative_value_eur", sa.Numeric(14, 2), nullable=True),
        sa.Column("extraction_confidence", sa.String(32), nullable=False, server_default="extracted"),
        sa.Column("raw_snippet", sa.Text(), nullable=True),
    )
    op.create_index("ix_line_items_period_category", "financial_line_items", ["filing_period_id", "line_item"])

    op.create_table(
        "computed_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filing_period_id", sa.Integer(), sa.ForeignKey("filing_periods.id"), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("metric_key", sa.String(64), nullable=False),
        sa.Column("metric_value", sa.Numeric(14, 4), nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("computed_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_computed_metrics_period_category", "computed_metrics", ["filing_period_id", "category"])

    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filing_period_id", sa.Integer(), sa.ForeignKey("filing_periods.id"), nullable=True),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="ceo"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("embeddings")
    op.drop_table("ai_insights")
    op.drop_table("computed_metrics")
    op.drop_table("financial_line_items")
    op.drop_table("filing_periods")
    op.drop_table("source_documents")
    op.drop_table("companies")
