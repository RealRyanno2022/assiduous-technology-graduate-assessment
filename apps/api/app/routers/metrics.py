from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.metrics import CategoryResponse, LineItemOut, MetricOut
from app.services import repository, role_access

router = APIRouter(tags=["metrics"])

_CATEGORIES = ["growth", "profitability", "cash_liquidity", "solvency", "returns"]
_PATHS = {
    "growth": "/growth",
    "profitability": "/profitability",
    "cash_liquidity": "/cash-liquidity",
    "solvency": "/solvency",
    "returns": "/returns",
}


def _build_response(db: Session, category: str, role: str) -> CategoryResponse:
    level = role_access.access_level(role, category)
    if level == "hidden":
        raise HTTPException(403, f"This category isn't part of the {role.replace('_', ' ')} view of the Board Report")

    period = repository.get_latest_filing_period(db)
    if period is None:
        raise HTTPException(404, "No filing period has been ingested yet - run the seed/extraction pipeline")

    metrics = repository.get_metrics_for_category(db, period.id, category)
    if level == "summary":
        allowed = set(role_access.summary_metric_keys(role, category) or [])
        metrics = [m for m in metrics if m.metric_key in allowed]

    line_items = repository.get_line_items(db, period.id, category)
    return CategoryResponse(
        period_label=period.period_label,
        period_start=period.period_start,
        period_end=period.period_end,
        is_audited=period.is_audited,
        access_level=level,
        metrics=[MetricOut(metric_key=m.metric_key, metric_value=float(m.metric_value), unit=m.unit) for m in metrics],
        line_items=[
            LineItemOut(
                statement=li.statement,
                line_item=li.line_item,
                value_eur=float(li.value_eur),
                comparative_value_eur=float(li.comparative_value_eur) if li.comparative_value_eur is not None else None,
                extraction_confidence=li.extraction_confidence,
            )
            for li in line_items
        ],
    )


for _category, _path in _PATHS.items():
    def _make_handler(category: str):
        def handler(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CategoryResponse:
            return _build_response(db, category, current_user.role)

        return handler

    router.get(_path, response_model=CategoryResponse)(_make_handler(_category))
