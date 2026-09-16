// NEXT_PUBLIC_API_URL always wins when actually set. Otherwise: a production build
// defaults to the deployed Render API rather than localhost, since a Vercel build
// silently proceeding with the wrong (dev) default is worse than this being wrong
// for the rare case someone runs `next build` locally against a non-default API.
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production" ? "https://senus-api-y1hy.onrender.com" : "http://localhost:8000");

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
  access_level: "full" | "summary";
  metrics: MetricOut[];
  line_items: LineItemOut[];
};
export type Role = "management" | "board" | "equity_investor" | "credit_provider";
export type InsightOut = { category: string; title: string; body: string; model: string };
export type ReportSection = { heading: string; body: string };
export type DirectorsReportResponse = { period_label: string; sections: ReportSection[]; model: string; generated_at: string };

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

export function getRole(): Role | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("senus_role") as Role | null;
}

export function getFullName(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("senus_full_name");
}

export function clearToken() {
  window.localStorage.removeItem("senus_token");
  window.localStorage.removeItem("senus_role");
  window.localStorage.removeItem("senus_full_name");
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
    // FastAPI error bodies are {"detail": "..."} - surface the message, not raw JSON
    let message = text || res.statusText;
    try {
      const parsed = JSON.parse(text);
      if (typeof parsed?.detail === "string") message = parsed.detail;
    } catch {
      // not JSON - fall back to the raw text already assigned above
    }
    throw new ApiError(res.status, message);
  }
  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<Role> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  if (!res.ok) throw new ApiError(res.status, "Incorrect email or password");
  const data = await res.json();
  setToken(data.access_token);
  window.localStorage.setItem("senus_role", data.role);
  window.localStorage.setItem("senus_full_name", data.full_name);
  return data.role as Role;
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
export const getDirectorsReport = (refresh = false) =>
  request<DirectorsReportResponse>(`/reports/directors-report${refresh ? "?refresh=true" : ""}`);
