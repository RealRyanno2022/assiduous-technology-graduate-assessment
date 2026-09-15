from app.services.role_access import ROLES, access_level, summary_metric_keys


def test_management_sees_everything_full():
    for category in ["growth", "profitability", "cash_liquidity", "solvency", "returns"]:
        assert access_level("management", category) == "full"


def test_credit_provider_returns_is_hidden():
    assert access_level("credit_provider", "returns") == "hidden"


def test_credit_provider_full_on_their_own_concerns():
    assert access_level("credit_provider", "cash_liquidity") == "full"
    assert access_level("credit_provider", "solvency") == "full"


def test_equity_investor_full_on_growth_and_returns_summary_on_balance_sheet():
    assert access_level("equity_investor", "growth") == "full"
    assert access_level("equity_investor", "returns") == "full"
    assert access_level("equity_investor", "cash_liquidity") == "summary"
    assert access_level("equity_investor", "solvency") == "summary"


def test_board_growth_is_summary_everything_else_full():
    assert access_level("board", "growth") == "summary"
    assert access_level("board", "profitability") == "full"


def test_summary_allowlist_only_defined_for_summary_tier_roles():
    for role in ROLES:
        for category in ["growth", "profitability", "cash_liquidity", "solvency", "returns"]:
            keys = summary_metric_keys(role, category)
            level = access_level(role, category)
            if keys is not None:
                assert level == "summary", f"{role}/{category} has a summary allowlist but access level is {level}"


def test_unknown_role_falls_back_to_management():
    assert access_level("nonexistent_role", "returns") == "full"
