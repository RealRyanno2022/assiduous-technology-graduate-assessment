from sqlalchemy.orm import Session

from app.models.computed_metric import ComputedMetric
from app.models.filing_period import FilingPeriod
from app.models.financial_line_item import FinancialLineItem

# Which source line items are relevant evidence for each Board Report category -
# several overlap (e.g. cash_and_cash_equivalents feeds both cash_liquidity and solvency)
CATEGORY_LINE_ITEMS: dict[str, list[str]] = {
    "growth": ["turnover", "gross_profit", "pipeline_closed_value_eur", "pipeline_open_value_eur", "enterprise_customers_closed"],
    "profitability": ["turnover", "cost_of_sales", "gross_profit", "administrative_expenses", "other_operating_income", "group_operating_loss"],
    "cash_liquidity": [
        "cash_and_cash_equivalents",
        "group_operating_loss",
        "movements_in_working_capital",
        "net_cash_used_in_operating_activities",
        "net_cash_used_in_investing_activities",
        "net_cash_inflow_from_financing_activities",
        "debtors",
        "creditors_due_within_one_year",
    ],
    "solvency": ["net_assets", "creditors_due_after_one_year", "cash_and_cash_equivalents", "group_operating_loss", "interest_payable"],
    "returns": ["group_operating_loss", "total_assets_less_current_liabilities"],
}


def get_latest_filing_period(db: Session, period_type: str = "HY") -> FilingPeriod | None:
    return (
        db.query(FilingPeriod)
        .filter(FilingPeriod.period_type == period_type)
        .order_by(FilingPeriod.period_end.desc())
        .first()
    )


def get_metrics_for_category(db: Session, filing_period_id: int, category: str) -> list[ComputedMetric]:
    return (
        db.query(ComputedMetric)
        .filter(ComputedMetric.filing_period_id == filing_period_id, ComputedMetric.category == category)
        .all()
    )


def get_all_metrics(db: Session, filing_period_id: int) -> list[ComputedMetric]:
    return db.query(ComputedMetric).filter(ComputedMetric.filing_period_id == filing_period_id).all()


def get_line_items(db: Session, filing_period_id: int, category: str | None = None) -> list[FinancialLineItem]:
    query = db.query(FinancialLineItem).filter(FinancialLineItem.filing_period_id == filing_period_id)
    if category and category in CATEGORY_LINE_ITEMS:
        query = query.filter(FinancialLineItem.line_item.in_(CATEGORY_LINE_ITEMS[category]))
    return query.all()
