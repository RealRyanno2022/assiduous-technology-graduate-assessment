from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class FinancialLineItem(Base):
    __tablename__ = "financial_line_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    filing_period_id: Mapped[int] = mapped_column(ForeignKey("filing_periods.id"))
    source_document_id: Mapped[int | None] = mapped_column(ForeignKey("source_documents.id"), nullable=True)
    statement: Mapped[str] = mapped_column(String(32))  # pnl | balance_sheet | cash_flow
    line_item: Mapped[str] = mapped_column(String(128))  # canonical key, e.g. "turnover"
    value_eur: Mapped[float] = mapped_column(Numeric(14, 2))
    comparative_value_eur: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    extraction_confidence: Mapped[str] = mapped_column(String(32), default="extracted")
    raw_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    filing_period = relationship("FilingPeriod", back_populates="line_items")
