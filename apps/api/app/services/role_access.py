# The brief names four Board Report readers - Management, the Board, Equity
# Investors and Credit Providers - with different concerns. This is a real,
# backend-enforced access policy (a role gets a 403, not just a hidden nav item),
# not cosmetic frontend filtering, per category:
#   "full"    - every computed metric for that category
#   "summary" - a curated headline subset (see SUMMARY_METRIC_ALLOWLIST)
#   "hidden"  - the category endpoint 403s for that role
#
# Nested by design: management sees everything; board sees everything except a
# couple of operational sales-tracking figures that are a day-to-day management
# concern, not a governance one; the two external parties each get full depth in
# their own area of concern and a headline-only view of the rest.
ROLES = ["management", "board", "equity_investor", "credit_provider"]

ROLE_ACCESS: dict[str, dict[str, str]] = {
    "management": {"growth": "full", "profitability": "full", "cash_liquidity": "full", "solvency": "full", "returns": "full"},
    "board": {"growth": "summary", "profitability": "full", "cash_liquidity": "full", "solvency": "full", "returns": "full"},
    "equity_investor": {"growth": "full", "profitability": "full", "cash_liquidity": "summary", "solvency": "summary", "returns": "full"},
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
    ("equity_investor", "cash_liquidity"): ["cash_and_equivalents_eur", "cash_runway_months"],
    ("equity_investor", "solvency"): ["net_assets_eur", "net_cash_position_eur"],
    ("credit_provider", "growth"): ["revenue_yoy_growth_pct", "revenue_eur"],
    ("credit_provider", "profitability"): ["gross_margin_pct", "ebitda_eur"],
}


def access_level(role: str, category: str) -> str:
    return ROLE_ACCESS.get(role, ROLE_ACCESS["management"]).get(category, "full")


def summary_metric_keys(role: str, category: str) -> list[str] | None:
    return SUMMARY_METRIC_ALLOWLIST.get((role, category))
