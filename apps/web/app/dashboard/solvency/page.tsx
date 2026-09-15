"use client";

import CategoryView from "@/components/CategoryView";
import { getSolvency } from "@/lib/api";
import type { CategoryResponse } from "@/lib/api";

export default function SolvencyPage() {
  return (
    <CategoryView
      title="Solvency & Leverage"
      description="Net assets, bank debt and debt service coverage."
      fetcher={getSolvency}
      dataGapNote="Debt Service Coverage Ratio here is EBITDA / interest expense - a simplified proxy, since the filing doesn't disclose a scheduled loan principal-repayment figure to use as the standard denominator (EBITDA / (interest + principal due))."
      chart="pie"
      pieTitle="Capital & reserves - composition of net assets"
      pieSlices={(data: CategoryResponse) => {
        const byKey = Object.fromEntries(data.line_items.map((li) => [li.line_item, li.value_eur]));
        return [
          { label: "Called up share capital", value: byKey["called_up_share_capital"] ?? 0 },
          { label: "Share premium", value: byKey["share_premium"] ?? 0 },
          { label: "Retained earnings", value: byKey["retained_earnings"] ?? 0 },
          // a pie slice can't be negative - retained earnings can go negative in a
          // loss-making prior period, so this composition only holds when all three
          // components are actually positive (true for HY2026, not guaranteed forever)
        ].filter((s) => s.value > 0);
      }}
    />
  );
}
