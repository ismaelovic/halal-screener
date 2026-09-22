import axios from "axios";

import type { CompanySummary, ScreeningResponse, SearchResponse } from "./types";

const BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 10_000,
});

export async function searchCompanies(query: string): Promise<CompanySummary[]> {
  const { data } = await apiClient.get<SearchResponse>("/companies/search", {
    params: { q: query },
  });
  return data.results;
}

export async function getScreening(symbol: string): Promise<ScreeningResponse> {
  const { data } = await apiClient.get<ScreeningResponse>(`/companies/${symbol}/screening`);
  return data;
}
