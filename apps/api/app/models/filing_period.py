from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class FilingPeriod(Base):
    __tablename__ = "filing_periods"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    source_document_id: Mapped[int | None] = mapped_column(ForeignKey("source_documents.id"), nullable=True)
    period_type: Mapped[str] = mapped_column(String(8))  # HY | FY
    period_label: Mapped[str] = mapped_column(String(32))  # e.g. "HY2026"
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    is_audited: Mapped[bool] = mapped_column(Boolean, default=False)

    company = relationship("Company", back_populates="filing_periods")
    line_items = relationship("FinancialLineItem", back_populates="filing_period")
    metrics = relationship("ComputedMetric", back_populates="filing_period")
    insights = relationship("AIInsight", back_populates="filing_period")
