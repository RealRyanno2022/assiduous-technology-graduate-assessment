from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    filing_period_id: Mapped[int | None] = mapped_column(ForeignKey("filing_periods.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(64))  # e.g. "claude-sonnet-5" or "offline-template"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    filing_period = relationship("FilingPeriod", back_populates="insights")
