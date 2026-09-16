import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import Company, ComputedMetric, FilingPeriod, FinancialLineItem, SourceDocument, User  # noqa: E402
from app.services import extraction  # noqa: E402
from app.services import metrics as metrics_service  # noqa: E402
from app.services.schema import failed_target_keys  # noqa: E402

# SOURCE_PDF_PATH lets the Docker image (which copies data/ to a flat /app/data path)
# override the local-dev default of walking up to the repo's data/raw/ directory.
# Computed lazily: the repo-relative walk-up only has enough parents to resolve in
# local dev - it would IndexError in Docker's flattened layout if ever evaluated there.
_source_pdf_path_env = os.environ.get("SOURCE_PDF_PATH")
PDF_PATH = (
    Path(_source_pdf_path_env)
    if _source_pdf_path_env
    else Path(__file__).resolve().parents[3] / "data" / "raw" / "senus_hy2026_results_pr.pdf"
)

# The FY25 full-year figures aren't in the HY2026 PR's financial statements - they're
# quoted narratively in its "Notes to editors" section as reference context only
FY25_CONTEXT_SNIPPET = (
    "For the year ended 30 June 2025, Senus recorded revenue of €836,991, "
    "serving 138 customer accounts."
)


def run():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        _seed_demo_user(db)
        company = _get_or_create_company(db)
        source_doc = _get_or_create_source_document(db, company)
        hy2026 = _seed_hy2026(db, company, source_doc)
        _seed_fy2025_context(db, company, source_doc, hy2026)
        print(f"Seed complete. Filing period HY2026 id={hy2026.id}")
    finally:
        db.close()


def _get_or_create_company(db) -> Company:
    company = db.query(Company).filter(Company.ticker == "SENUS").first()
    if company:
        return company
    company = Company(name="Senus PLC", ticker="SENUS", isin="IE000O0F49R3", country="Ireland", sector="Natural Capital / ClimateTech")
    db.add(company)
    db.commit()
    return company


def _get_or_create_source_document(db, company: Company) -> SourceDocument:
    existing = db.query(SourceDocument).filter(SourceDocument.file_path == str(PDF_PATH)).first()
    if existing:
        return existing
    doc = SourceDocument(
        company_id=company.id,
        doc_type="half_year_pr",
        title="Senus PLC Half Year Results for the 6 months ended 31 December 2025",
        file_path=str(PDF_PATH),
        published_date=dt.date(2026, 3, 19),
    )
    db.add(doc)
    db.commit()
    return doc


def _seed_hy2026(db, company: Company, source_doc: SourceDocument) -> FilingPeriod:
    period = db.query(FilingPeriod).filter(FilingPeriod.period_label == "HY2026").first()
    if period:
        db.query(FinancialLineItem).filter(FinancialLineItem.filing_period_id == period.id).delete()
    else:
        period = FilingPeriod(
            company_id=company.id,
            source_document_id=source_doc.id,
            period_type="HY",
            period_label="HY2026",
            period_start=dt.date(2025, 7, 1),
            period_end=dt.date(2025, 12, 31),
            is_audited=False,
        )
        db.add(period)
        db.commit()

    items, method = extraction.extract(str(PDF_PATH))
    print(f"Extracted {len(items)} line items via '{method}' pipeline")
    failed_keys = failed_target_keys(items)
    if failed_keys:
        print(f"WARNING: reconciliation failed for: {failed_keys} - marking as failed_validation")

    for item in items:
        confidence = "failed_validation" if item.line_item in failed_keys else "extracted"
        db.add(
            FinancialLineItem(
                filing_period_id=period.id,
                source_document_id=source_doc.id,
                statement=item.statement,
                line_item=item.line_item,
                value_eur=item.value_eur,
                comparative_value_eur=item.comparative_value_eur,
                extraction_confidence=confidence,
                raw_snippet=item.raw_snippet,
            )
        )
    db.commit()

    db.query(ComputedMetric).filter(ComputedMetric.filing_period_id == period.id).delete()
    db.commit()

    li = {i.line_item: i.value_eur for i in items if i.line_item not in failed_keys}
    comp = {i.line_item: i.comparative_value_eur for i in items if i.comparative_value_eur is not None}
    for m in metrics_service.compute_all(li, comp):
        db.add(
            ComputedMetric(
                filing_period_id=period.id, category=m.category, metric_key=m.metric_key, metric_value=m.metric_value, unit=m.unit
            )
        )
    db.commit()
    return period


def _seed_fy2025_context(db, company: Company, source_doc: SourceDocument, hy2026: FilingPeriod):
    period = db.query(FilingPeriod).filter(FilingPeriod.period_label == "FY2025").first()
    if not period:
        period = FilingPeriod(
            company_id=company.id,
            source_document_id=source_doc.id,
            period_type="FY",
            period_label="FY2025",
            period_start=dt.date(2024, 7, 1),
            period_end=dt.date(2025, 6, 30),
            is_audited=False,
        )
        db.add(period)
        db.commit()
    db.query(FinancialLineItem).filter(FinancialLineItem.filing_period_id == period.id).delete()
    db.add_all(
        [
            FinancialLineItem(
                filing_period_id=period.id,
                source_document_id=source_doc.id,
                statement="pnl",
                line_item="turnover",
                value_eur=836_991,
                extraction_confidence="reference_only",
                raw_snippet=FY25_CONTEXT_SNIPPET,
            ),
            FinancialLineItem(
                filing_period_id=period.id,
                source_document_id=source_doc.id,
                statement="kpi",
                line_item="customer_accounts",
                value_eur=138,
                extraction_confidence="reference_only",
                raw_snippet=FY25_CONTEXT_SNIPPET,
            ),
        ]
    )
    db.commit()

    db.query(ComputedMetric).filter(
        ComputedMetric.filing_period_id == hy2026.id, ComputedMetric.metric_key.in_(["fy25_full_year_revenue_eur", "fy25_customer_accounts"])
    ).delete()
    db.add_all(
        [
            ComputedMetric(filing_period_id=hy2026.id, category="growth", metric_key="fy25_full_year_revenue_eur", metric_value=836_991, unit="eur"),
            ComputedMetric(filing_period_id=hy2026.id, category="growth", metric_key="fy25_customer_accounts", metric_value=138, unit="count"),
        ]
    )
    db.commit()


# One demo account per Board Report reader the brief names - each gets a role-scoped
# view enforced server-side (see app/services/role_access.py), not just a relabeled login
_DEMO_USERS = [
    ("management@senus.com", "Brendan Allen", "management"),
    ("board@senus.com", "Gerard Keenan", "board"),
    ("investor@senus.com", "Equity Investor", "equity_investor"),
    ("lender@senus.com", "Credit Provider", "credit_provider"),
]


def _seed_demo_user(db):
    for email, full_name, role in _DEMO_USERS:
        if db.query(User).filter(User.email == email).first():
            continue
        db.add(User(email=email, hashed_password=hash_password("senus2030"), full_name=full_name, role=role))
    db.commit()


if __name__ == "__main__":
    run()
