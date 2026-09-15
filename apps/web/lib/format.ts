export function formatMetric(value: number, unit: string): string {
  switch (unit) {
    case "eur":
      return new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);
    case "pct":
      return `${value >= 0 ? "" : ""}${value.toFixed(1)}%`;
    case "months":
      return `${value.toFixed(1)} mo`;
    case "ratio":
      return `${value.toFixed(2)}x`;
    case "count":
      return value.toLocaleString("en-IE");
    default:
      return value.toString();
  }
}

// line_item rows carry a "value_eur" column even for non-currency KPIs (customer/deal
// counts) - the API doesn't tag a unit per line item, so the count-shaped keys are
// named here rather than assumed to be EUR like every other line item
const COUNT_LINE_ITEMS = new Set(["enterprise_customers_closed", "customer_accounts", "deals_closed_final_two_months"]);

export function formatLineItemValue(lineItem: string, value: number): string {
  return formatMetric(value, COUNT_LINE_ITEMS.has(lineItem) ? "count" : "eur");
}

// Metrics where the figure's sign genuinely means "good"/"bad" (growth, margins,
// EBITDA, cash, ROCE). Everything else (magnitudes, cost ratios, debt balances,
// pipeline counts) is presented neutrally - a positive cost-of-sales % isn't "good",
// it's just a ratio, so it must not borrow the same status color as real performance
const SIGN_COLORED_METRICS = new Set([
  "revenue_yoy_growth_pct",
  "gross_profit_yoy_growth_pct",
  "gross_margin_pct",
  "gross_margin_pct_prior",
  "operating_margin_pct",
  "ebitda_eur",
  "ebitda_margin_pct",
  "free_cash_flow_eur",
  "net_cash_position_eur",
  "roce_pct",
]);

export function metricTone(metricKey: string, value: number): "good" | "bad" | "neutral" {
  if (!SIGN_COLORED_METRICS.has(metricKey)) return "neutral";
  return value >= 0 ? "good" : "bad";
}

export function metricLabel(key: string): string {
  return key
    .replace(/_eur$|_pct$|_months$|_ratio$/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
