"use client";

import CategoryView from "@/components/CategoryView";
import { getSolvency } from "@/lib/api";

export default function SolvencyPage() {
  return (
    <CategoryView
      title="Solvency & Leverage"
      description="Net assets, bank debt and debt service coverage."
      fetcher={getSolvency}
      dataGapNote="Debt Service Coverage Ratio here is EBITDA / interest expense - a simplified proxy, since the filing doesn't disclose a scheduled loan principal-repayment figure to use as the standard denominator (EBITDA / (interest + principal due))."
    />
  );
}
