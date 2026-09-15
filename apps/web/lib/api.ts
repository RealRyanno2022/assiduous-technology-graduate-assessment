const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type MetricOut = { metric_key: string; metric_value: number; unit: string };
export type LineItemOut = {
  statement: string;
  line_item: string;
  value_eur: number;
  comparative_value_eur: number | null;
  extraction_confidence: string;
};
export type CategoryResponse = {
  period_label: string;
  period_start: string;
  period_end: string;
  is_audited: boolean;
  metrics: MetricOut[];
  line_items: LineItemOut[];
};
export type InsightOut = { category: string; title: string; body: string; model: string };

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("senus_token");
}

export function setToken(token: string) {
  window.localStorage.setItem("senus_token", token);
}

export function clearToken() {
  window.localStorage.removeItem("senus_token");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(res.status, text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<string> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  if (!res.ok) throw new ApiError(res.status, "Incorrect email or password");
  const data = await res.json();
  setToken(data.access_token);
  return data.access_token;
}

export const getGrowth = () => request<CategoryResponse>("/growth");
export const getProfitability = () => request<CategoryResponse>("/profitability");
export const getCashLiquidity = () => request<CategoryResponse>("/cash-liquidity");
export const getSolvency = () => request<CategoryResponse>("/solvency");
export const getReturns = () => request<CategoryResponse>("/returns");
export const getInsights = () => request<InsightOut[]>("/insights");
export const askInsights = (question: string) =>
  request<{ answer: string; model: string }>("/insights/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
