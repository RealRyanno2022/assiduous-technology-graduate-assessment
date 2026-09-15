from app.services.metrics import compute_all, compute_cash_liquidity, compute_growth, compute_profitability, compute_solvency

# Real figures from the HY2026 PR (current period, comparative HY25)
HY2026 = {
    "turnover": 354_813,
    "cost_of_sales": 64_861,
    "gross_profit": 289_952,
    "administrative_expenses": 781_975,
    "other_operating_income": 8_269,
    "group_operating_loss": 483_753,
    "interest_payable": 1_391,
    "loss_before_taxation": 485_144,
    "net_assets": 561_081,
    # both are printed as negative figures on the balance sheet (they're liabilities)
    "creditors_due_after_one_year": -76_474,
    "cash_and_cash_equivalents": 735_189,
    "net_cash_used_in_operating_activities": -410_291,
    "debtors": 188_149,
    "creditors_due_within_one_year": -387_105,
    "total_assets_less_current_liabilities": 637_554,
    "movements_in_working_capital": 64_839,
    "net_cash_used_in_investing_activities": -8_500,
    "pipeline_closed_value_eur": 700_000,
    "pipeline_open_value_eur": 500_000,
    "enterprise_customers_closed": 21,
}
HY25_COMPARATIVE = {"turnover": 340_931, "gross_profit": 272_331}


def test_revenue_yoy_growth_matches_press_release():
    metrics = {m.metric_key: m.metric_value for m in compute_growth(HY2026, HY25_COMPARATIVE)}
    assert round(metrics["revenue_yoy_growth_pct"], 1) == 4.1


def test_gross_margin_matches_press_release():
    metrics = {m.metric_key: m.metric_value for m in compute_profitability(HY2026, HY25_COMPARATIVE)}
    assert round(metrics["gross_margin_pct"], 1) == 81.7
    # PR headline rounds this to 79.8%; recomputing from the reported absolute figures
    # gives 79.9% - a documented rounding discrepancy, not an extraction error
    assert round(metrics["gross_margin_pct_prior"], 1) == 79.9


def test_ebitda_adds_back_depreciation_to_operating_loss():
    metrics = {m.metric_key: m.metric_value for m in compute_profitability(HY2026, HY25_COMPARATIVE)}
    # Cash flow statement shows loss + interest + depreciation = -473,739
    assert round(metrics["ebitda_eur"]) == -473_739


def test_cash_runway_is_positive_given_positive_cash_and_negative_operating_cash_flow():
    metrics = {m.metric_key: m.metric_value for m in compute_cash_liquidity(HY2026)}
    assert metrics["cash_runway_months"] > 0
    assert round(metrics["cash_runway_months"], 1) == round(735_189 / (410_291 / 6), 1)


def test_compute_all_returns_metrics_across_every_category():
    metrics = compute_all(HY2026, HY25_COMPARATIVE)
    categories = {m.category for m in metrics}
    assert categories == {"growth", "profitability", "cash_liquidity", "solvency", "returns"}


def test_missing_denominator_does_not_raise():
    assert compute_growth({}, {}) == []
    assert compute_cash_liquidity({}) == []


def test_bank_debt_and_working_capital_flip_the_balance_sheets_negative_sign():
    solvency = {m.metric_key: m.metric_value for m in compute_solvency(HY2026)}
    liquidity = {m.metric_key: m.metric_value for m in compute_cash_liquidity(HY2026)}
    # matches the PR's own "Cash and bank debt balances were €735.1k and €76.5k" framing
    assert solvency["bank_debt_eur"] == 76_474
    assert round(solvency["net_cash_position_eur"]) == 658_715
    assert round(liquidity["working_capital_ex_contingent_eur"]) == 536_233


def test_ebitda_to_free_cash_flow_bridge():
    liquidity = {m.metric_key: m.metric_value for m in compute_cash_liquidity(HY2026)}
    assert round(liquidity["ebitda_eur"]) == -473_739
    assert liquidity["working_capital_movement_eur"] == 64_839
    assert liquidity["net_investing_cash_flow_eur"] == -8_500
    # operating cash flow + investing cash flow, matching the cash flow statement's own arithmetic
    assert round(liquidity["free_cash_flow_eur"]) == -418_791


def test_bookings_and_pipeline_surface_as_growth_metrics():
    metrics = {m.metric_key: m.metric_value for m in compute_growth(HY2026, HY25_COMPARATIVE)}
    assert metrics["bookings_closed_eur"] == 700_000
    assert metrics["pipeline_open_eur"] == 500_000
    assert metrics["enterprise_customers_closed"] == 21
