import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.generated_report import GeneratedReport
from app.routers.deps import get_current_user
from app.schemas.metrics import DirectorsReportResponse, ReportSection
from app.services import repository
from app.services.directors_report import generate_directors_report

router = APIRouter(prefix="/reports", dependencies=[Depends(get_current_user)], tags=["reports"])

_CATEGORIES = ["growth", "profitability", "cash_liquidity", "solvency", "returns"]


@router.get("/directors-report", response_model=DirectorsReportResponse)
def get_directors_report(db: Session = Depends(get_db), refresh: bool = False):
    period = repository.get_latest_filing_period(db)
    if period is None:
        raise HTTPException(404, "No filing period has been ingested yet - run the seed/extraction pipeline")

    existing = (
        db.query(GeneratedReport)
        .filter(GeneratedReport.filing_period_id == period.id, GeneratedReport.report_type == "directors_report")
        .order_by(GeneratedReport.created_at.desc())
        .first()
    )
    if existing and not refresh:
        sections = json.loads(existing.sections_json)
        return DirectorsReportResponse(
            period_label=period.period_label,
            sections=[ReportSection(**s) for s in sections],
            model=existing.model,
            generated_at=existing.created_at,
        )

    metrics_by_category = {c: {m.metric_key: float(m.metric_value) for m in repository.get_metrics_for_category(db, period.id, c)} for c in _CATEGORIES}
    line_items = {li.line_item: float(li.value_eur) for li in repository.get_line_items(db, period.id)}
    sections, model = generate_directors_report(period.period_label, metrics_by_category, line_items)

    record = GeneratedReport(filing_period_id=period.id, report_type="directors_report", sections_json=json.dumps(sections), model=model)
    db.add(record)
    db.commit()
    db.refresh(record)

    return DirectorsReportResponse(
        period_label=period.period_label,
        sections=[ReportSection(**s) for s in sections],
        model=model,
        generated_at=record.created_at,
    )
