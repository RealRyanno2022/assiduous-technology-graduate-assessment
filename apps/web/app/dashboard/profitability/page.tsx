"use client";

import CategoryView from "@/components/CategoryView";
import { getProfitability } from "@/lib/api";
import type { CategoryResponse } from "@/lib/api";

export default function ProfitabilityPage() {
  return (
    <CategoryView
      title="Profitability"
      description="Gross margin, operating margin, EBITDA margin and the cost structure driving them."
      fetcher={getProfitability}
      chart="pie"
      pieTitle="Cost breakdown - share of total costs"
      pieSlices={(data: CategoryResponse) => {
        const byKey = Object.fromEntries(data.line_items.map((li) => [li.line_item, li.value_eur]));
        return [
          { label: "Cost of sales", value: byKey["cost_of_sales"] ?? 0 },
          { label: "Administrative expenses", value: byKey["administrative_expenses"] ?? 0 },
        ];
      }}
    />
  );
}
