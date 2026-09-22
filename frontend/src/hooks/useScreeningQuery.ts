import { useQuery } from "@tanstack/react-query";

import { getScreening, searchCompanies } from "../api/client";

export function useCompanySearchQuery(query: string) {
  return useQuery({
    queryKey: ["companies", "search", query],
    queryFn: () => searchCompanies(query),
    enabled: query.trim().length > 0,
  });
}

export function useScreeningQuery(symbol: string | undefined) {
  return useQuery({
    queryKey: ["screening", symbol],
    queryFn: () => getScreening(symbol as string),
    enabled: Boolean(symbol),
  });
}
