from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ComputedMetric(Base):
    __tablename__ = "computed_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    filing_period_id: Mapped[int] = mapped_column(ForeignKey("filing_periods.id"))
    category: Mapped[str] = mapped_column(String(32))  # growth | profitability | cash_liquidity | solvency | returns
    metric_key: Mapped[str] = mapped_column(String(64))
    metric_value: Mapped[float] = mapped_column(Numeric(14, 4))
    unit: Mapped[str] = mapped_column(String(16))  # eur | pct | ratio | months | days
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    filing_period = relationship("FilingPeriod", back_populates="metrics")
