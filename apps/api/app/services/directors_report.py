import json
import logging
import re

from app.core.config import settings

logger = logging.getLogger(__name__)

# Section order and headings mirror the structure of a real half-year Directors'/
# Chairman's statement (see the Senus HY2026 PR itself: highlights, financial review,
# commercial progress, going concern, outlook) - the point of this feature is to give
# the Director a draft they can lightly edit for public correspondence, in the voice
# and shape their own filings already use, not a generic AI summary
SECTION_ORDER = ["Overview", "Financial Review", "Commercial Progress", "Cash Position & Going Concern", "Outlook"]

_SYSTEM_PROMPT = """You draft the narrative sections of a company's half-year Directors'
Report for a small listed company, in the register of a genuine RNS/PR statement (see
the tone of "Group Revenue increased X% to..." style disclosures) - factual, measured,
not promotional.
You are given the period label and a JSON payload of computed metrics and source line
items across every category. Return ONLY a JSON object with exactly these keys, each a
string of 2-4 sentences: "Overview", "Financial Review", "Commercial Progress",
"Cash Position & Going Concern", "Outlook".
Use only the figures in the payload - never invent a number. If the payload doesn't
cover something a section would normally mention, write around it rather than making it up.
"""


def generate_directors_report(period_label: str, metrics: dict[str, dict[str, float]], line_items: dict[str, float]) -> tuple[list[dict], str]:
    if settings.anthropic_api_key:
        try:
            return _generate_with_llm(period_label, metrics, line_items), settings.anthropic_model
        except Exception:
            logger.exception("LLM Directors' Report generation failed, falling back to offline template")
    return _generate_offline(period_label, metrics, line_items), "offline-template"


def _generate_with_llm(period_label: str, metrics: dict[str, dict[str, float]], line_items: dict[str, float]) -> list[dict]:
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    payload = {"period_label": period_label, "metrics": metrics, "line_items": line_items}
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1200,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    raw = response.content[0].text
    if raw is None:
        raise ValueError(f"LLM returned no text content (stop_reason={response.stop_reason})")
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    sections = json.loads(raw)
    return [{"heading": h, "body": sections[h]} for h in SECTION_ORDER if h in sections]


def _generate_offline(period_label: str, metrics: dict[str, dict[str, float]], line_items: dict[str, float]) -> list[dict]:
    g, p, cl, s, r = (metrics.get(c, {}) for c in ["growth", "profitability", "cash_liquidity", "solvency", "returns"])

    overview = (
        f"The Directors present the Group's results for {period_label}. Revenue grew "
        f"{g.get('revenue_yoy_growth_pct', 0):.1f}% year-on-year to €{g.get('revenue_eur', 0):,.0f}, with gross margin "
        f"of {p.get('gross_margin_pct', 0):.1f}%. The Group remains loss-making at the operating line as it continues "
        f"to invest ahead of the Senus 2030 growth strategy."
    )

    financial_review = (
        f"Gross profit grew {g.get('gross_profit_yoy_growth_pct', 0):.1f}% year-on-year, with gross margin improving "
        f"to {p.get('gross_margin_pct', 0):.1f}% (prior period: {p.get('gross_margin_pct_prior', 0):.1f}%). EBITDA for "
        f"the period was €{p.get('ebitda_eur', 0):,.0f}. Administrative expenses were "
        f"{p.get('admin_expenses_pct_of_revenue', 0):.1f}% of revenue as the Group continued to build out its team and "
        f"technology capability, in line with its scale-up strategy."
    )

    commercial_progress = (
        f"Commercial momentum continued in the period, with approximately €{g.get('bookings_closed_eur', 0):,.0f} of "
        f"pipeline value closed across {g.get('enterprise_customers_closed', 0):.0f} enterprise customers, and a "
        f"further approximately €{g.get('pipeline_open_eur', 0):,.0f} of pipeline remaining open. The Directors view "
        f"this pipeline as a positive indicator for the Group's continued growth trajectory."
    )

    cash_and_going_concern = (
        f"The Group held cash of €{cl.get('cash_and_equivalents_eur', 0):,.0f} at period end against bank debt of "
        f"€{s.get('bank_debt_eur', 0):,.0f}, a net cash position of €{s.get('net_cash_position_eur', 0):,.0f}. At the "
        f"current rate of operating cash consumption this represents approximately {cl.get('cash_runway_months', 0):.1f} "
        f"months of runway. The Directors note that the Group's cash position reflects financing activity in the "
        f"period rather than operating cash generation, and have prepared these statements on a going concern basis "
        f"having considered the Group's funding position and pipeline."
    )

    # never hardcode the strategy targets - only cite them when actually extracted
    # for this filing, otherwise write around them rather than assume they still hold
    cagr = line_items.get("strategy_cagr_target_pct")
    ebitda_fy = line_items.get("strategy_ebitda_positive_target_fy")
    if cagr is not None and ebitda_fy is not None:
        target_sentence = (
            f"Under its Senus 2030 strategy, the Group continues to target sales growth at a compound annual rate of "
            f"no less than {cagr:.0f}% and anticipates becoming EBITDA positive during FY{ebitda_fy:.0f}. "
        )
        approach_clause = f"as the commercial pipeline converts and the Group approaches its FY{ebitda_fy:.0f} EBITDA-positive target."
    else:
        target_sentence = ""
        approach_clause = "as the commercial pipeline converts and the Group scales toward profitability."
    outlook = (
        f"{target_sentence}Return on capital employed ({r.get('roce_pct', 0):.1f}%) is not yet a meaningful measure of "
        f"performance while the Group remains pre-scale and investing for growth; the Board expects this to improve "
        f"{approach_clause}"
    )

    bodies = {
        "Overview": overview,
        "Financial Review": financial_review,
        "Commercial Progress": commercial_progress,
        "Cash Position & Going Concern": cash_and_going_concern,
        "Outlook": outlook,
    }
    return [{"heading": h, "body": bodies[h]} for h in SECTION_ORDER]
