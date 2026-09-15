"use client";

import CategoryView from "@/components/CategoryView";
import { getProfitability } from "@/lib/api";

export default function ProfitabilityPage() {
  return (
    <CategoryView
      title="Profitability"
      description="Gross margin, operating margin, EBITDA margin and the cost structure driving them."
      fetcher={getProfitability}
    />
  );
}
