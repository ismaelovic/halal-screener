import AsyncStorage from "@react-native-async-storage/async-storage";
import { useCallback, useEffect, useState } from "react";

import type { Verdict } from "../api/types";

const STORAGE_KEY = "halal-screener:recently-screened";
const MAX_RECENTS = 8;

export interface RecentEntry {
  ticker: string;
  exchange: string;
  name: string;
  verdict: Verdict;
}

function keyOf(entry: Pick<RecentEntry, "ticker" | "exchange">): string {
  return `${entry.ticker}.${entry.exchange}`;
}

export function useRecentlyScreened() {
  const [recents, setRecents] = useState<RecentEntry[]>([]);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((raw) => {
      if (raw) {
        setRecents(JSON.parse(raw));
      }
    });
  }, []);

  const addRecent = useCallback((entry: RecentEntry) => {
    setRecents((prev) => {
      const deduped = prev.filter((r) => keyOf(r) !== keyOf(entry));
      const next = [entry, ...deduped].slice(0, MAX_RECENTS);
      AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  return { recents, addRecent };
}
