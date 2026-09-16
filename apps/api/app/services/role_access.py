# The brief names four Board Report readers - Management, the Board, Equity
# Investors and Credit Providers - with different concerns. This is a real,
# backend-enforced access policy (a role gets a 403, not just a hidden nav item),
# not cosmetic frontend filtering, per category:
#   "full"    - every computed metric for that category
#   "summary" - a curated headline subset (see SUMMARY_METRIC_ALLOWLIST)
#   "hidden"  - the category endpoint 403s for that role
#
# Least-privilege by design: every role gets full depth only where its category-level
# need actually requires it, headline-only where context is useful but detail isn't,
# and hidden where a category has no bearing on that reader's concern at all.
#   Management (CEO) - full operational visibility everywhere, the only role that does.
#   Board - governance oversight, not line-item audit: full on cash/solvency/returns
#     (going-concern is a core fiduciary duty), headline-only on growth and
#     profitability (operational trend detail is a management concern, not governance).
#   Equity Investor - their upside case: full on growth and returns (what drives the
#     investment thesis), headline-only on profitability, cash and solvency.
#   Credit Provider - repayment risk: full on cash/solvency (the actual credit
#     assessment), headline-only on growth/profitability for context, returns hidden
#     entirely since ROCE has no bearing on debt serviceability.
ROLES = ["management", "board", "equity_investor", "credit_provider"]

ROLE_ACCESS: dict[str, dict[str, str]] = {
    "management": {"growth": "full", "profitability": "full", "cash_liquidity": "full", "solvency": "full", "returns": "full"},
    "board": {"growth": "summary", "profitability": "summary", "cash_liquidity": "full", "solvency": "full", "returns": "full"},
    "equity_investor": {"growth": "full", "profitability": "summary", "cash_liquidity": "summary", "solvency": "summary", "returns": "full"},
    "credit_provider": {"growth": "summary", "profitability": "summary", "cash_liquidity": "full", "solvency": "full", "returns": "hidden"},
}

# (role, category) -> metric_keys shown when that category is "summary" for the role.
# Board loses the FY25 historical-reference figures (a management/IR concern, not a
# governance one) but keeps the rest of growth at full depth otherwise.
SUMMARY_METRIC_ALLOWLIST: dict[tuple[str, str], list[str]] = {
    ("board", "growth"): [
        "revenue_yoy_growth_pct",
        "revenue_eur",
        "gross_profit_yoy_growth_pct",
        "bookings_closed_eur",
        "pipeline_open_eur",
        "enterprise_customers_closed",
    ],
    ("board", "profitability"): ["gross_margin_pct", "ebitda_eur"],
    ("equity_investor", "profitability"): ["gross_margin_pct", "ebitda_eur"],
    ("equity_investor", "cash_liquidity"): ["cash_and_equivalents_eur", "cash_runway_months"],
    ("equity_investor", "solvency"): ["net_assets_eur", "net_cash_position_eur"],
    ("credit_provider", "growth"): ["revenue_yoy_growth_pct", "revenue_eur"],
    ("credit_provider", "profitability"): ["gross_margin_pct", "ebitda_eur"],
}


def access_level(role: str, category: str) -> str:
    return ROLE_ACCESS.get(role, ROLE_ACCESS["management"]).get(category, "full")


def summary_metric_keys(role: str, category: str) -> list[str] | None:
    return SUMMARY_METRIC_ALLOWLIST.get((role, category))
