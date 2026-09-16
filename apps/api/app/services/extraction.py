import json
import logging
import re

from pypdf import PdfReader

from app.core.config import settings
from app.services.schema import LINE_ITEM_KEYS, ExtractedLineItem

logger = logging.getLogger(__name__)

# Maps a canonical key to the label(s) as printed in the Senus HY2026 PR, in statement order
_OFFLINE_LABELS: dict[str, tuple[str, list[str]]] = {
    "turnover": ("pnl", ["Turnover"]),
    "cost_of_sales": ("pnl", ["Cost of sales"]),
    "gross_profit": ("pnl", ["Gross Profit"]),
    "distribution_costs": ("pnl", ["Distribution costs"]),
    "administrative_expenses": ("pnl", ["Administrative expenses"]),
    "other_operating_income": ("pnl", ["Other operating income"]),
    "group_operating_loss": ("pnl", ["Group operating loss"]),
    "interest_payable": ("pnl", ["Interest payable and similar expenses"]),
    "loss_before_taxation": ("pnl", ["Loss before taxation"]),
    "tax_expense": ("pnl", ["Tax expense"]),
    "loss_for_the_period": ("pnl", ["Loss for the period"]),
    "goodwill": ("balance_sheet", ["Goodwill"]),
    "development_costs": ("balance_sheet", ["Development Costs"]),
    "tangible_assets": ("balance_sheet", ["Tangible Assets"]),
    "debtors": ("balance_sheet", ["Debtors"]),
    "cash_and_cash_equivalents": ("balance_sheet", ["Cash and cash equivalents"]),
    "creditors_due_within_one_year": ("balance_sheet", ["Creditors: amounts falling due within one year"]),
    "contingent_consideration": ("balance_sheet", ["Contingent consideration"]),
    "net_current_assets": ("balance_sheet", ["Net Current Assets"]),
    "total_assets_less_current_liabilities": ("balance_sheet", ["Total Assets Less Current Liabilities"]),
    "creditors_due_after_one_year": ("balance_sheet", ["Creditors: amounts falling due after more than one year"]),
    "net_assets": ("balance_sheet", ["Net (liabilities) / Assets"]),
    "called_up_share_capital": ("balance_sheet", ["Called up share capital presented as equity"]),
    "share_premium": ("balance_sheet", ["Share Premium"]),
    "retained_earnings": ("balance_sheet", ["Retained Earnings"]),
    "movements_in_working_capital": ("cash_flow", ["Movements in working capital"]),
    "net_cash_used_in_operating_activities": ("cash_flow", ["Net Cash used in operating activities"]),
    "net_cash_used_in_investing_activities": ("cash_flow", ["Net Cash used in investment activities"]),
    "net_cash_inflow_from_financing_activities": ("cash_flow", ["Net Cash inflow from financing activities"]),
    "net_increase_in_cash": ("cash_flow", ["Net (decrease) / increase in cash and cash equivalents"]),
    "cash_at_beginning_of_period": ("cash_flow", ["Cash and cash equivalent at beginning of period"]),
    "cash_at_end_of_period": ("cash_flow", ["Cash and cash equivalent at end of period"]),
}

_NUMBER = r"-?[\d,]+(?:\.\d+)?"

# Section markers in the PR that bound each statement's table, so a label like
# "Turnover" or "Group operating loss" (which also appears in the prose highlights,
# with abbreviated €k figures) is only matched inside its actual statement table
_SECTION_MARKERS = {
    "pnl": ("Consolidated Profit and Loss Account", "Consolidated Balance Sheet"),
    "balance_sheet": ("Consolidated Balance Sheet", "Consolidated cash flow statement"),
    "cash_flow": ("Consolidated cash flow statement", "Notes to the Half Year Report"),
}


def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _section_text(text: str, statement: str) -> str:
    start_marker, end_marker = _SECTION_MARKERS[statement]
    start = text.find(start_marker)
    if start == -1:
        return ""
    start += len(start_marker)
    end = text.find(end_marker, start)
    section = text[start:end] if end != -1 else text[start:]
    return " ".join(section.split())  # collapse the PDF's line-wrapping to single spaces


def extract_offline(text: str) -> list[ExtractedLineItem]:
    # Deterministic fallback: within each statement's own section, finds a label
    # followed by its two trailing figures (current period, comparative) - the PDF
    # wraps some labels/numbers across lines, hence operating on whitespace-normalised
    # section text rather than raw lines. Works with zero external calls.
    items: list[ExtractedLineItem] = []
    normalized_by_statement = {s: _section_text(text, s) for s in _SECTION_MARKERS}

    for key, (statement, labels) in _OFFLINE_LABELS.items():
        if statement == "kpi":
            continue
        section = normalized_by_statement.get(statement, "")
        for label in labels:
            # the comparative figure is optional - some HY26-only lines (e.g. the
            # Loamin contingent consideration) print just one figure, not two
            match = re.search(rf"{re.escape(label)}\s+({_NUMBER})(?:\s+({_NUMBER}))?", section)
            if not match:
                continue
            value = float(match.group(1).replace(",", ""))
            comparative = float(match.group(2).replace(",", "")) if match.group(2) else None
            items.append(
                ExtractedLineItem(
                    statement=statement,
                    line_item=key,
                    value_eur=value,
                    comparative_value_eur=comparative,
                    raw_snippet=match.group(0),
                )
            )
            break
    return items


# Bookings/pipeline facts live in the Highlights prose, not the statement tables - a
# table parser can never reach these, which is the concrete case ADR 0001 argues for
# LLM extraction on. These handful of regexes stand in for that narrative-extraction
# step for the one filing we have today; run unconditionally (both extraction paths
# get them) since they're cheap and don't need a model call
_PIPELINE_PATTERN = re.compile(
    r"pipeline deals of approx\.\s*€([\d.]+)k across (\d+) enterprise customers closed in the period "
    r"\(further approx\.\s*€([\d.]+)k of open pipeline\)"
)
_DEALS_CLOSED_PATTERN = re.compile(
    r"closed (\d+) commercial deals in the final two months of \d{4}, with a combined estimated value of approx\.\s*€([\d.]+)k"
)
_CAGR_TARGET_PATTERN = re.compile(r"compound annual growth rate of no less than (\d+)%")
_EBITDA_TARGET_PATTERN = re.compile(r"anticipating becoming EBITDA positive during FY(\d{4})")


def extract_narrative_kpis(text: str) -> list[ExtractedLineItem]:
    normalized = " ".join(text.split())
    items: list[ExtractedLineItem] = []

    match = _PIPELINE_PATTERN.search(normalized)
    if match:
        closed_k, customers, open_k = match.groups()
        items.append(
            ExtractedLineItem(statement="kpi", line_item="pipeline_closed_value_eur", value_eur=float(closed_k) * 1000, raw_snippet=match.group(0))
        )
        items.append(
            ExtractedLineItem(statement="kpi", line_item="enterprise_customers_closed", value_eur=float(customers), raw_snippet=match.group(0))
        )
        items.append(
            ExtractedLineItem(statement="kpi", line_item="pipeline_open_value_eur", value_eur=float(open_k) * 1000, raw_snippet=match.group(0))
        )

    match = _DEALS_CLOSED_PATTERN.search(normalized)
    if match:
        deals, value_k = match.groups()
        items.append(
            ExtractedLineItem(statement="kpi", line_item="deals_closed_final_two_months", value_eur=float(deals), raw_snippet=match.group(0))
        )
        items.append(
            ExtractedLineItem(
                statement="kpi", line_item="deals_closed_final_two_months_value_eur", value_eur=float(value_k) * 1000, raw_snippet=match.group(0)
            )
        )

    match = _CAGR_TARGET_PATTERN.search(normalized)
    if match:
        items.append(ExtractedLineItem(statement="kpi", line_item="strategy_cagr_target_pct", value_eur=float(match.group(1)), raw_snippet=match.group(0)))

    match = _EBITDA_TARGET_PATTERN.search(normalized)
    if match:
        items.append(
            ExtractedLineItem(statement="kpi", line_item="strategy_ebitda_positive_target_fy", value_eur=float(match.group(1)), raw_snippet=match.group(0))
        )
    return items


_SYSTEM_PROMPT = """You extract financial line items from a company results announcement.
Return ONLY a JSON array of objects, each with exactly these fields:
statement (one of: pnl, balance_sheet, cash_flow),
line_item (one canonical key from the allowed list below),
value_eur (number, the current-period figure, no currency symbol or thousands separators),
comparative_value_eur (number or null, the prior-period comparative figure if printed on the same line),
raw_snippet (the exact line of text the figures came from).

Only extract figures that are explicitly printed in the document. Do not infer, round,
or compute derived figures yourself. If a line item is not present, omit it.

Allowed line_item keys by statement:
""" + json.dumps(LINE_ITEM_KEYS, indent=2)


def extract_with_llm(text: str) -> list[ExtractedLineItem]:
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=8000,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    raw = response.content[0].text
    if raw is None:
        raise ValueError(f"LLM returned no text content (stop_reason={response.stop_reason})")
    # Models sometimes wrap JSON in a fenced code block; strip that if present
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    payload = json.loads(raw)
    return [ExtractedLineItem(**row) for row in payload]


def extract(pdf_path: str) -> tuple[list[ExtractedLineItem], str]:
    text = extract_pdf_text(pdf_path)
    if settings.anthropic_api_key:
        try:
            items, method = extract_with_llm(text), "llm"
        except Exception:
            # The offline parser is a real fallback, not a placeholder - every AI
            # path in this app is meant to degrade gracefully, not take the whole
            # ingestion run down with it.
            logger.exception("LLM extraction failed, falling back to offline parser")
            items, method = extract_offline(text), "offline"
    else:
        items, method = extract_offline(text), "offline"
    return [*items, *extract_narrative_kpis(text)], method
