from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    filing_period_id: Mapped[int] = mapped_column(ForeignKey("filing_periods.id"))
    report_type: Mapped[str] = mapped_column(String(32))  # e.g. "directors_report"
    sections_json: Mapped[str] = mapped_column(Text)  # [{"heading": str, "body": str}, ...]
    model: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    filing_period = relationship("FilingPeriod")
