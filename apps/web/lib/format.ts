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

export function metricLabel(key: string): string {
  return key
    .replace(/_eur$|_pct$|_months$|_ratio$/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
