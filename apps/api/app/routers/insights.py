from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.ai_insight import AIInsight
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.metrics import InsightOut, QARequest, QAResponse
from app.services import insights as insights_service
from app.services import repository, role_access

router = APIRouter(prefix="/insights", tags=["insights"])

_CATEGORIES = ["growth", "profitability", "cash_liquidity", "solvency", "returns"]


@router.get("", response_model=list[InsightOut])
def get_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), refresh: bool = False):
    period = repository.get_latest_filing_period(db)
    if period is None:
        raise HTTPException(404, "No filing period has been ingested yet - run the seed/extraction pipeline")

    visible_categories = [c for c in _CATEGORIES if role_access.access_level(current_user.role, c) != "hidden"]
    results: list[InsightOut] = []
    for category in visible_categories:
        existing = (
            db.query(AIInsight)
            .filter(AIInsight.filing_period_id == period.id, AIInsight.category == category)
            .order_by(AIInsight.created_at.desc())
            .first()
        )
        if existing and not refresh:
            results.append(InsightOut(category=category, title=existing.title, body=existing.body, model=existing.model))
            continue

        metrics = {m.metric_key: float(m.metric_value) for m in repository.get_metrics_for_category(db, period.id, category)}
        line_items = {li.line_item: float(li.value_eur) for li in repository.get_line_items(db, period.id, category)}
        body, model = insights_service.generate_insight(category, metrics, line_items)
        title = category.replace("_", " ").title()
        record = AIInsight(filing_period_id=period.id, category=category, title=title, body=body, model=model)
        db.add(record)
        db.commit()
        results.append(InsightOut(category=category, title=title, body=body, model=model))
    return results


@router.post("/ask", response_model=QAResponse)
def ask_question(payload: QARequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    period = repository.get_latest_filing_period(db)
    if period is None:
        raise HTTPException(404, "No filing period has been ingested yet - run the seed/extraction pipeline")

    # ground the answer only in what this role is allowed to see - a credit provider's
    # Q&A shouldn't leak ROCE detail that's hidden from their dashboard
    visible_categories = [c for c in _CATEGORIES if role_access.access_level(current_user.role, c) != "hidden"]
    all_metrics: dict[str, dict[str, float]] = {}
    for category in visible_categories:
        all_metrics[category] = {
            m.metric_key: float(m.metric_value) for m in repository.get_metrics_for_category(db, period.id, category)
        }
    line_items = {li.line_item: float(li.value_eur) for li in repository.get_line_items(db, period.id)}
    answer, model = insights_service.answer_question(payload.question, all_metrics, line_items)
    return QAResponse(answer=answer, model=model)
