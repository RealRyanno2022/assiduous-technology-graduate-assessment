"use client";

import CategoryView from "@/components/CategoryView";
import { getReturns } from "@/lib/api";

export default function ReturnsPage() {
  return (
    <CategoryView
      title="Returns"
      description="Return on capital employed (ROCE) - a metric that is not yet meaningful for a pre-scale business, and the AI commentary says so."
      fetcher={getReturns}
    />
  );
}
