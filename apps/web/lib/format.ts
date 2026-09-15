export function formatMetric(value: number, unit: string): string {
  switch (unit) {
    case "eur":
      return new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);
    case "pct":
      return `${value.toFixed(1)}%`;
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

// Hand-authored display names - deliberately not derived from the API's snake_case
// keys, which read as database fields ("Ebitda", "Fy25 Full Year Revenue") rather
// than something written for a Board reader
const METRIC_LABELS: Record<string, string> = {
  revenue_yoy_growth_pct: "Revenue growth (YoY)",
  revenue_eur: "Revenue",
  gross_profit_yoy_growth_pct: "Gross profit growth (YoY)",
  bookings_closed_eur: "Bookings closed",
  pipeline_open_eur: "Open pipeline",
  enterprise_customers_closed: "Enterprise customers won",
  fy25_full_year_revenue_eur: "FY2025 revenue (full year)",
  fy25_customer_accounts: "FY2025 customer accounts",
  gross_margin_pct: "Gross margin",
  gross_margin_pct_prior: "Gross margin (prior period)",
  operating_margin_pct: "Operating margin",
  ebitda_eur: "EBITDA",
  ebitda_margin_pct: "EBITDA margin",
  cost_of_sales_pct_of_revenue: "Cost of sales (% of revenue)",
  admin_expenses_pct_of_revenue: "Admin expenses (% of revenue)",
  cash_and_equivalents_eur: "Cash & equivalents",
  net_operating_cash_flow_eur: "Operating cash flow",
  cash_runway_months: "Cash runway",
  working_capital_ex_contingent_eur: "Working capital",
  working_capital_movement_eur: "Working capital movement",
  net_investing_cash_flow_eur: "Investing cash flow",
  free_cash_flow_eur: "Free cash flow",
  net_assets_eur: "Net assets",
  bank_debt_eur: "Bank debt",
  net_cash_position_eur: "Net cash position",
  debt_service_coverage_ratio: "Debt service coverage",
  roce_pct: "Return on capital employed",
};

const LINE_ITEM_LABELS: Record<string, string> = {
  turnover: "Turnover",
  cost_of_sales: "Cost of sales",
  gross_profit: "Gross profit",
  distribution_costs: "Distribution costs",
  administrative_expenses: "Administrative expenses",
  other_operating_income: "Other operating income",
  group_operating_loss: "Group operating loss",
  interest_payable: "Interest payable",
  loss_before_taxation: "Loss before taxation",
  tax_expense: "Tax expense",
  loss_for_the_period: "Loss for the period",
  goodwill: "Goodwill",
  development_costs: "Development costs",
  tangible_assets: "Tangible assets",
  debtors: "Debtors",
  cash_and_cash_equivalents: "Cash and cash equivalents",
  creditors_due_within_one_year: "Creditors due within one year",
  contingent_consideration: "Contingent consideration",
  net_current_assets: "Net current assets",
  total_assets_less_current_liabilities: "Total assets less current liabilities",
  creditors_due_after_one_year: "Creditors due after one year",
  net_assets: "Net assets",
  called_up_share_capital: "Called-up share capital",
  share_premium: "Share premium",
  retained_earnings: "Retained earnings",
  movements_in_working_capital: "Movements in working capital",
  net_cash_used_in_operating_activities: "Net cash used in operating activities",
  net_cash_used_in_investing_activities: "Net cash used in investing activities",
  net_cash_inflow_from_financing_activities: "Net cash inflow from financing activities",
  net_increase_in_cash: "Net increase in cash",
  cash_at_beginning_of_period: "Cash at beginning of period",
  cash_at_end_of_period: "Cash at end of period",
  customer_accounts: "Customer accounts",
  pipeline_closed_value_eur: "Pipeline closed (value)",
  pipeline_open_value_eur: "Pipeline open (value)",
  enterprise_customers_closed: "Enterprise customers closed",
  deals_closed_final_two_months: "Deals closed (final 2 months)",
  deals_closed_final_two_months_value_eur: "Deals closed value (final 2 months)",
  strategy_cagr_target_pct: "Senus 2030 CAGR target",
  strategy_ebitda_positive_target_fy: "EBITDA-positive target year",
};

const STATEMENT_LABELS: Record<string, string> = {
  pnl: "Income statement",
  balance_sheet: "Balance sheet",
  cash_flow: "Cash flow statement",
  kpi: "Key metric",
};

const CONFIDENCE_LABELS: Record<string, string> = {
  extracted: "Verified",
  reference_only: "Reference only",
  failed_validation: "Needs review",
};

export function metricLabel(key: string): string {
  return (
    METRIC_LABELS[key] ??
    key
      .replace(/_eur$|_pct$|_months$|_ratio$/, "")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

export function lineItemLabel(key: string): string {
  return LINE_ITEM_LABELS[key] ?? key.replace(/_/g, " ");
}

export function statementLabel(key: string): string {
  return STATEMENT_LABELS[key] ?? key;
}

export function confidenceLabel(key: string): string {
  return CONFIDENCE_LABELS[key] ?? key;
}
