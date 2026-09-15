import json

from app.core.config import settings

_SYSTEM_PROMPT = """You are a financial analyst writing commentary for a Board Report.
You are given a category name and a JSON payload of the computed metrics and source
line items for that category, for a single reporting period of Senus PLC.
Write 2-4 sentences of commentary a CEO/Board member would find useful: state the
headline number, note the direction/trend, and flag anything a careful reader should
know that the number alone doesn't show (e.g. cash driven by financing not operations,
or a margin that isn't yet meaningful because the business is pre-scale).
Do not invent figures that are not in the payload. Be direct, not promotional."""

# Deterministic phrasing used when no LLM key is configured - same inputs, no API call
_OFFLINE_TEMPLATES = {
    "growth": lambda m: (
        f"Revenue grew {m.get('revenue_yoy_growth_pct', 0):.1f}% year-on-year to "
        f"€{m.get('revenue_eur', 0):,.0f}. Growth is real but modest, consistent with "
        f"management's note of a weather-delayed soil sampling season."
    ),
    "profitability": lambda m: (
        f"Gross margin is {m.get('gross_margin_pct', 0):.1f}% (vs {m.get('gross_margin_pct_prior', 0):.1f}% prior "
        f"period), a structurally strong unit economics story. The group is still loss-making at the "
        f"operating line ({m.get('operating_margin_pct', 0):.1f}% operating margin) because it is investing "
        f"ahead of the Senus 2030 scale-up, not because the core product is unprofitable."
    ),
    "cash_liquidity": lambda m: (
        f"Cash of €{m.get('cash_and_equivalents_eur', 0):,.0f} gives roughly "
        f"{m.get('cash_runway_months', 0):.1f} months of runway at the current operating burn rate. This "
        f"cash position is healthy largely because of the €1.1m equity raise completed in the period, "
        f"not because operations are cash generative - operating cash flow remains negative."
    ),
    "solvency": lambda m: (
        f"The company is net cash positive (€{m.get('net_cash_position_eur', 0):,.0f} cash net of bank debt), "
        f"which is the right way to read solvency here rather than a debt service coverage ratio - that ratio "
        f"is not yet meaningful while EBITDA is negative."
    ),
    "returns": lambda m: (
        f"ROCE is {m.get('roce_pct', 0):.1f}%, and is not yet a meaningful measure of performance: the group "
        f"is pre-scale and investing for growth under Senus 2030, so capital employed is not yet being asked "
        f"to produce a return."
    ),
}


def generate_insight(category: str, metrics: dict[str, float], line_items: dict[str, float]) -> tuple[str, str]:
    if settings.anthropic_api_key:
        return _generate_with_llm(category, metrics, line_items), settings.anthropic_model
    template = _OFFLINE_TEMPLATES.get(category)
    body = template(metrics) if template else f"No commentary template available for '{category}'."
    return body, "offline-template"


def _generate_with_llm(category: str, metrics: dict[str, float], line_items: dict[str, float]) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    payload = {"category": category, "metrics": metrics, "line_items": line_items}
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=400,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    return response.content[0].text.strip()


_QA_SYSTEM_PROMPT = """You are a financial analyst assistant answering ad-hoc questions
about Senus PLC's Board Report. You are given the full set of computed metrics and
extracted line items across all categories for the latest reporting period. Answer the
user's question using only this data. If the data doesn't cover the question, say so
rather than guessing."""


def answer_question(question: str, all_metrics: dict[str, dict[str, float]], all_line_items: dict[str, float]) -> tuple[str, str]:
    if not settings.anthropic_api_key:
        return (
            "AI Q&A requires ANTHROPIC_API_KEY to be configured - this endpoint has no offline "
            "fallback because free-form questions can't be answered from a fixed template.",
            "offline-unavailable",
        )
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    payload = {"metrics": all_metrics, "line_items": all_line_items, "question": question}
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=500,
        system=_QA_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    return response.content[0].text.strip(), settings.anthropic_model
