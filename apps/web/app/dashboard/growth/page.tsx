"use client";

import CategoryView from "@/components/CategoryView";
import { getGrowth } from "@/lib/api";

export default function GrowthPage() {
  return (
    <CategoryView
      title="Growth & Revenue"
      description="Revenue, gross profit and customer base momentum vs. the prior comparable period."
      fetcher={getGrowth}
      dataGapNote="Month-on-month trend and a per-channel (direct vs. intermediary) revenue split are not disclosed in the HY2026 filing - only the half-year vs. half-year comparison is derivable from the two periods it reports. Extending to monthly/channel granularity needs a source document with that breakdown."
    />
  );
}
