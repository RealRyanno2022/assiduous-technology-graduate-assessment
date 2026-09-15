from app.services.directors_report import SECTION_ORDER, generate_directors_report

METRICS = {
    "growth": {
        "revenue_yoy_growth_pct": 4.0718,
        "revenue_eur": 354_813,
        "gross_profit_yoy_growth_pct": 6.4704,
        "bookings_closed_eur": 700_000,
        "pipeline_open_eur": 500_000,
        "enterprise_customers_closed": 21,
    },
    "profitability": {"gross_margin_pct": 81.7197, "gross_margin_pct_prior": 79.8786, "ebitda_eur": -473_739, "admin_expenses_pct_of_revenue": 220.39},
    "cash_liquidity": {"cash_and_equivalents_eur": 735_189, "cash_runway_months": 10.75},
    "solvency": {"bank_debt_eur": 76_474, "net_cash_position_eur": 658_715},
    "returns": {"roce_pct": -151.75},
}
LINE_ITEMS = {"strategy_cagr_target_pct": 50, "strategy_ebitda_positive_target_fy": 2028}


def test_offline_report_has_every_section_in_order():
    sections, model = generate_directors_report("HY2026", METRICS, LINE_ITEMS)
    assert model == "offline-template"
    assert [s["heading"] for s in sections] == SECTION_ORDER


def test_offline_report_cites_real_figures_not_placeholders():
    sections, _ = generate_directors_report("HY2026", METRICS, LINE_ITEMS)
    full_text = " ".join(s["body"] for s in sections)
    assert "354,813" in full_text
    assert "81.7%" in full_text
    assert "700,000" in full_text
    assert "10.8" in full_text or "10.7" in full_text


def test_offline_report_outlook_cites_strategy_targets_when_available():
    sections, _ = generate_directors_report("HY2026", METRICS, LINE_ITEMS)
    outlook = next(s["body"] for s in sections if s["heading"] == "Outlook")
    assert "50%" in outlook
    assert "FY2028" in outlook


def test_offline_report_outlook_degrades_gracefully_without_strategy_targets():
    sections, _ = generate_directors_report("HY2026", METRICS, {})
    outlook = next(s["body"] for s in sections if s["heading"] == "Outlook")
    assert "FY" not in outlook.split(".")[0]  # no fabricated target when not extracted
