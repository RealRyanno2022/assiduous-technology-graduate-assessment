"use client";

import CategoryView from "@/components/CategoryView";
import { getCashLiquidity } from "@/lib/api";

export default function CashLiquidityPage() {
  return (
    <CategoryView
      title="Cash & Liquidity"
      description="Cash on hand, operating cash burn, runway and working capital."
      fetcher={getCashLiquidity}
    />
  );
}
