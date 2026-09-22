import { StyleSheet, Text, View } from "react-native";

import type { Verdict } from "../api/types";

const VERDICT_COPY: Record<Verdict, { label: string; color: string; background: string }> = {
  halal: { label: "Halal", color: "#1b5e20", background: "#e3f6e5" },
  haram: { label: "Haram", color: "#8c1d1d", background: "#fbe4e4" },
  questionable: { label: "Questionable", color: "#8a6d00", background: "#fdf3d8" },
};

interface VerdictCardProps {
  name: string;
  ticker: string;
  verdict: Verdict;
}

export function VerdictCard({ name, ticker, verdict }: VerdictCardProps) {
  const copy = VERDICT_COPY[verdict];

  return (
    <View style={[styles.container, { backgroundColor: copy.background }]}>
      <Text style={styles.ticker}>{ticker}</Text>
      <Text style={styles.name}>{name}</Text>
      <Text style={[styles.verdict, { color: copy.color }]}>{copy.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    padding: 20,
    alignItems: "center",
    gap: 4,
  },
  ticker: {
    fontSize: 14,
    color: "#555",
  },
  name: {
    fontSize: 20,
    fontWeight: "600",
  },
  verdict: {
    fontSize: 28,
    fontWeight: "800",
    marginTop: 8,
  },
});
