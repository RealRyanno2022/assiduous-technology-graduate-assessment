from collections.abc import Callable

from pydantic import BaseModel

# Canonical line-item keys the extractor is allowed to emit, grouped by statement
LINE_ITEM_KEYS = {
    "pnl": [
        "turnover",
        "cost_of_sales",
        "gross_profit",
        "distribution_costs",
        "administrative_expenses",
        "other_operating_income",
        "group_operating_loss",
        "interest_payable",
        "loss_before_taxation",
        "tax_expense",
        "loss_for_the_period",
    ],
    "balance_sheet": [
        "goodwill",
        "development_costs",
        "tangible_assets",
        "debtors",
        "cash_and_cash_equivalents",
        "creditors_due_within_one_year",
        "contingent_consideration",
        "net_current_assets",
        "total_assets_less_current_liabilities",
        "creditors_due_after_one_year",
        "net_assets",
        "called_up_share_capital",
        "share_premium",
        "retained_earnings",
    ],
    "cash_flow": [
        "movements_in_working_capital",
        "net_cash_used_in_operating_activities",
        "net_cash_used_in_investing_activities",
        "net_cash_inflow_from_financing_activities",
        "net_increase_in_cash",
        "cash_at_beginning_of_period",
        "cash_at_end_of_period",
    ],
    "kpi": [
        "customer_accounts",
        "pipeline_closed_value_eur",
        "pipeline_open_value_eur",
        "enterprise_customers_closed",
        "deals_closed_final_two_months",
        "deals_closed_final_two_months_value_eur",
        "strategy_cagr_target_pct",
        "strategy_ebitda_positive_target_fy",
    ],
}


class ExtractedLineItem(BaseModel):
    statement: str
    line_item: str
    value_eur: float
    comparative_value_eur: float | None = None
    raw_snippet: str


class ReconciliationFailure(BaseModel):
    rule: str
    detail: str
    target_key: str  # the derived line_item this check was validating


# Each rule: (name, target derived key, fn computing the expected value from by_key)
_RULES: list[tuple[str, str, Callable[[dict[str, float]], float | None]]] = [
    (
        "turnover - cost_of_sales == gross_profit",
        "gross_profit",
        lambda k: k["turnover"] - k["cost_of_sales"] if "turnover" in k and "cost_of_sales" in k else None,
    ),
    (
        # group_operating_loss is printed as a positive loss magnitude, not a signed
        # result, so it equals costs minus income rather than income minus costs
        "admin_expenses - gross_profit - other_income == operating_loss",
        "group_operating_loss",
        lambda k: k.get("administrative_expenses", 0) - k["gross_profit"] - k.get("other_operating_income", 0)
        if "gross_profit" in k
        else None,
    ),
    (
        "operating_loss + interest == loss_before_tax",
        "loss_before_taxation",
        lambda k: k["group_operating_loss"] + k.get("interest_payable", 0) if "group_operating_loss" in k else None,
    ),
    (
        "net_assets == share_capital + share_premium + retained_earnings",
        "net_assets",
        lambda k: k["called_up_share_capital"] + k["share_premium"] + k["retained_earnings"]
        if "called_up_share_capital" in k
        else None,
    ),
]


def reconcile(items: list[ExtractedLineItem], tolerance: float = 1.0) -> list[ReconciliationFailure]:
    # Cross-checks each derived figure against its components; flags rather than trusts
    by_key = {i.line_item: i.value_eur for i in items}
    failures: list[ReconciliationFailure] = []
    for rule, target_key, expected_fn in _RULES:
        expected = expected_fn(by_key)
        actual = by_key.get(target_key)
        if expected is None or actual is None:
            continue
        if abs(expected - actual) > tolerance:
            failures.append(
                ReconciliationFailure(
                    rule=rule, target_key=target_key, detail=f"expected {expected}, got {actual} (diff {expected - actual:.2f})"
                )
            )
    return failures


def failed_target_keys(items: list[ExtractedLineItem], tolerance: float = 1.0) -> set[str]:
    return {f.target_key for f in reconcile(items, tolerance)}
