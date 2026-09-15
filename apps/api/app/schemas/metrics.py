from datetime import date

from pydantic import BaseModel


class MetricOut(BaseModel):
    metric_key: str
    metric_value: float
    unit: str


class LineItemOut(BaseModel):
    statement: str
    line_item: str
    value_eur: float
    comparative_value_eur: float | None
    extraction_confidence: str


class CategoryResponse(BaseModel):
    period_label: str
    period_start: date
    period_end: date
    is_audited: bool
    metrics: list[MetricOut]
    line_items: list[LineItemOut]


class InsightOut(BaseModel):
    category: str
    title: str
    body: str
    model: str


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str
    model: str
