from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    ticker: Mapped[str] = mapped_column(String(32))
    isin: Mapped[str] = mapped_column(String(32))
    country: Mapped[str] = mapped_column(String(64))
    sector: Mapped[str] = mapped_column(String(128))

    filing_periods = relationship("FilingPeriod", back_populates="company")
    source_documents = relationship("SourceDocument", back_populates="company")
