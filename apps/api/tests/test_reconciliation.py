from app.services.schema import ExtractedLineItem, failed_target_keys, reconcile

GOOD_ITEMS = [
    ExtractedLineItem(statement="pnl", line_item="turnover", value_eur=354_813, raw_snippet="x"),
    ExtractedLineItem(statement="pnl", line_item="cost_of_sales", value_eur=64_861, raw_snippet="x"),
    ExtractedLineItem(statement="pnl", line_item="gross_profit", value_eur=289_952, raw_snippet="x"),
]


def test_consistent_figures_pass_reconciliation():
    assert reconcile(GOOD_ITEMS) == []


def test_inconsistent_figures_are_flagged():
    corrupted = [*GOOD_ITEMS[:2], ExtractedLineItem(statement="pnl", line_item="gross_profit", value_eur=999_999, raw_snippet="x")]
    failures = reconcile(corrupted)
    assert len(failures) == 1
    assert failures[0].target_key == "gross_profit"


def test_failed_target_keys_returns_empty_set_when_nothing_wrong():
    assert failed_target_keys(GOOD_ITEMS) == set()


def test_missing_component_is_skipped_not_flagged():
    # gross_profit alone, with no turnover/cost_of_sales to check it against
    assert reconcile([GOOD_ITEMS[2]]) == []
