export interface CompanySummary {
  ticker: string;
  exchange: string;
  name: string;
  sector: string | null;
  industry: string | null;
}

export interface SearchResponse {
  results: CompanySummary[];
}

export interface RatioBreakdown {
  value: number;
  threshold: number;
  passed: boolean;
}

export type BusinessActivityStatus = "compliant" | "non_compliant" | "review";

export interface BusinessActivity {
  status: BusinessActivityStatus;
  sector: string | null;
  industry: string | null;
}

export type Verdict = "halal" | "haram" | "questionable";

export interface ScreeningResponse {
  ticker: string;
  name: string;
  verdict: Verdict;
  screened_at: string;
  business_activity: BusinessActivity;
  debt_ratio: RatioBreakdown;
  cash_ratio: RatioBreakdown;
  purification_pct: number | null;
  flagged_reasons: string[];
  disclaimer: string;
}
