from pathlib import Path

from app.services.extraction import extract_narrative_kpis, extract_offline, extract_pdf_text

PDF_PATH = Path(__file__).resolve().parents[3] / "data" / "raw" / "senus_hy2026_results_pr.pdf"


def test_pdf_text_extraction_contains_known_figures():
    text = extract_pdf_text(str(PDF_PATH))
    assert "354,813" in text
    assert "Turnover" in text


def test_offline_extractor_reads_turnover_and_comparative():
    text = extract_pdf_text(str(PDF_PATH))
    items = extract_offline(text)
    turnover = next(i for i in items if i.line_item == "turnover")
    assert turnover.value_eur == 354_813
    assert turnover.comparative_value_eur == 340_931


def test_offline_extractor_reads_balance_sheet_net_assets():
    text = extract_pdf_text(str(PDF_PATH))
    items = extract_offline(text)
    net_assets = next(i for i in items if i.line_item == "net_assets")
    assert net_assets.value_eur == 561_081
    assert net_assets.comparative_value_eur == 173_316


def test_offline_extractor_output_passes_reconciliation():
    from app.services.schema import failed_target_keys

    text = extract_pdf_text(str(PDF_PATH))
    items = extract_offline(text)
    assert failed_target_keys(items) == set()


def test_offline_extractor_reads_working_capital_movement():
    text = extract_pdf_text(str(PDF_PATH))
    items = extract_offline(text)
    wc = next(i for i in items if i.line_item == "movements_in_working_capital")
    assert wc.value_eur == 64_839
    assert wc.comparative_value_eur == -53_584


def test_narrative_kpis_extracts_bookings_and_pipeline():
    text = extract_pdf_text(str(PDF_PATH))
    items = extract_narrative_kpis(text)
    by_key = {i.line_item: i.value_eur for i in items}
    assert by_key["pipeline_closed_value_eur"] == 700_000
    assert by_key["pipeline_open_value_eur"] == 500_000
    assert by_key["enterprise_customers_closed"] == 21
    assert by_key["deals_closed_final_two_months"] == 10
    assert by_key["deals_closed_final_two_months_value_eur"] == 425_000
