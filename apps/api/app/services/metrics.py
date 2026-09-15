from dataclasses import dataclass


@dataclass
class Metric:
    category: str
    metric_key: str
    metric_value: float
    unit: str


def _pct(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return (numerator / denominator) * 100


def _yoy(current: float | None, prior: float | None) -> float | None:
    if current is None or prior is None or prior == 0:
        return None
    return ((current - prior) / abs(prior)) * 100


def compute_growth(li: dict[str, float], comp: dict[str, float]) -> list[Metric]:
    turnover, turnover_prior = li.get("turnover"), comp.get("turnover")
    gross_profit, gross_profit_prior = li.get("gross_profit"), comp.get("gross_profit")
    metrics = []
    if (v := _yoy(turnover, turnover_prior)) is not None:
        metrics.append(Metric("growth", "revenue_yoy_growth_pct", v, "pct"))
    if turnover is not None:
        metrics.append(Metric("growth", "revenue_eur", turnover, "eur"))
    if (v := _yoy(gross_profit, gross_profit_prior)) is not None:
        metrics.append(Metric("growth", "gross_profit_yoy_growth_pct", v, "pct"))

    # bookings/pipeline - disclosed narratively in the PR, not a statement line, so
    # these come through only when extract_narrative_kpis found them (see extraction.py)
    if (v := li.get("pipeline_closed_value_eur")) is not None:
        metrics.append(Metric("growth", "bookings_closed_eur", v, "eur"))
    if (v := li.get("pipeline_open_value_eur")) is not None:
        metrics.append(Metric("growth", "pipeline_open_eur", v, "eur"))
    if (v := li.get("enterprise_customers_closed")) is not None:
        metrics.append(Metric("growth", "enterprise_customers_closed", v, "count"))
    return metrics


def compute_profitability(li: dict[str, float], comp: dict[str, float], depreciation: float = 10_014) -> list[Metric]:
    turnover = li.get("turnover")
    gross_profit = li.get("gross_profit")
    operating_loss = li.get("group_operating_loss")
    admin = li.get("administrative_expenses")
    cost_of_sales = li.get("cost_of_sales")
    metrics = []

    if (v := _pct(gross_profit, turnover)) is not None:
        metrics.append(Metric("profitability", "gross_margin_pct", v, "pct"))
    if (v := _pct(comp.get("gross_profit"), comp.get("turnover"))) is not None:
        metrics.append(Metric("profitability", "gross_margin_pct_prior", v, "pct"))
    if operating_loss is not None and turnover:
        metrics.append(Metric("profitability", "operating_margin_pct", -_pct(operating_loss, turnover), "pct"))
    if operating_loss is not None:
        ebitda = -operating_loss + depreciation  # operating_loss is stored positive (a loss), EBITDA adds back D&A
        metrics.append(Metric("profitability", "ebitda_eur", ebitda, "eur"))
        if turnover:
            metrics.append(Metric("profitability", "ebitda_margin_pct", _pct(ebitda, turnover), "pct"))
    if cost_of_sales is not None and turnover:
        metrics.append(Metric("profitability", "cost_of_sales_pct_of_revenue", _pct(cost_of_sales, turnover), "pct"))
    if admin is not None and turnover:
        metrics.append(Metric("profitability", "admin_expenses_pct_of_revenue", _pct(admin, turnover), "pct"))
    return metrics


def compute_cash_liquidity(li: dict[str, float], period_months: int = 6, depreciation: float = 10_014) -> list[Metric]:
    cash = li.get("cash_and_cash_equivalents")
    op_cash_flow = li.get("net_cash_used_in_operating_activities")
    current_assets_proxy = (li.get("debtors") or 0) + (cash or 0)
    # printed as a negative figure on the balance sheet (a liability); take the magnitude
    creditors_within_year = li.get("creditors_due_within_one_year")
    operating_loss = li.get("group_operating_loss")
    working_capital_movement = li.get("movements_in_working_capital")
    investing_cash_flow = li.get("net_cash_used_in_investing_activities")
    metrics = []

    if cash is not None:
        metrics.append(Metric("cash_liquidity", "cash_and_equivalents_eur", cash, "eur"))
    if op_cash_flow is not None:
        metrics.append(Metric("cash_liquidity", "net_operating_cash_flow_eur", op_cash_flow, "eur"))
        monthly_burn = -op_cash_flow / period_months
        if cash is not None and monthly_burn > 0:
            metrics.append(Metric("cash_liquidity", "cash_runway_months", cash / monthly_burn, "months"))
    if creditors_within_year is not None:
        # working capital excluding the one-off Loamin contingent consideration liability
        working_capital = current_assets_proxy - abs(creditors_within_year)
        metrics.append(Metric("cash_liquidity", "working_capital_ex_contingent_eur", working_capital, "eur"))

    # EBITDA -> operating cash flow -> free cash flow bridge
    if operating_loss is not None:
        metrics.append(Metric("cash_liquidity", "ebitda_eur", -operating_loss + depreciation, "eur"))
    if working_capital_movement is not None:
        metrics.append(Metric("cash_liquidity", "working_capital_movement_eur", working_capital_movement, "eur"))
    if investing_cash_flow is not None:
        metrics.append(Metric("cash_liquidity", "net_investing_cash_flow_eur", investing_cash_flow, "eur"))
    if op_cash_flow is not None and investing_cash_flow is not None:
        metrics.append(Metric("cash_liquidity", "free_cash_flow_eur", op_cash_flow + investing_cash_flow, "eur"))
    return metrics


def compute_solvency(li: dict[str, float]) -> list[Metric]:
    net_assets = li.get("net_assets")
    # printed as a negative figure on the balance sheet (a liability); take the magnitude
    bank_debt = abs(li["creditors_due_after_one_year"]) if "creditors_due_after_one_year" in li else None
    cash = li.get("cash_and_cash_equivalents")
    operating_loss = li.get("group_operating_loss")
    interest = li.get("interest_payable")
    metrics = []

    if net_assets is not None:
        metrics.append(Metric("solvency", "net_assets_eur", net_assets, "eur"))
    if bank_debt is not None:
        metrics.append(Metric("solvency", "bank_debt_eur", bank_debt, "eur"))
    if cash is not None and bank_debt is not None:
        metrics.append(Metric("solvency", "net_cash_position_eur", cash - bank_debt, "eur"))
    if operating_loss is not None and interest and interest != 0:
        ebitda = -operating_loss + 10_014
        metrics.append(Metric("solvency", "debt_service_coverage_ratio", ebitda / interest, "ratio"))
    return metrics


def compute_returns(li: dict[str, float], period_months: int = 6) -> list[Metric]:
    operating_loss = li.get("group_operating_loss")
    total_assets_less_current_liabilities = li.get("total_assets_less_current_liabilities")
    metrics = []

    if operating_loss is not None and total_assets_less_current_liabilities:
        annualised_operating_result = -operating_loss * (12 / period_months)
        roce = _pct(annualised_operating_result, total_assets_less_current_liabilities)
        metrics.append(Metric("returns", "roce_pct", roce, "pct"))
    return metrics


def compute_all(li: dict[str, float], comp: dict[str, float]) -> list[Metric]:
    return [
        *compute_growth(li, comp),
        *compute_profitability(li, comp),
        *compute_cash_liquidity(li),
        *compute_solvency(li),
        *compute_returns(li),
    ]
