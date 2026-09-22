import { StyleSheet, Text, View } from "react-native";

import type { BusinessActivity, RatioBreakdown as RatioBreakdownType } from "../api/types";

interface RatioBreakdownProps {
  businessActivity: BusinessActivity;
  debtRatio: RatioBreakdownType;
  cashRatio: RatioBreakdownType;
  flaggedReasons: string[];
}

function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function RatioBreakdown({
  businessActivity,
  debtRatio,
  cashRatio,
  flaggedReasons,
}: RatioBreakdownProps) {
  return (
    <View style={styles.container}>
      <Row
        label="Business activity"
        value={businessActivity.status.replace("_", " ")}
        passed={businessActivity.status === "compliant"}
      />
      <Row
        label={`Debt ratio (< ${formatPct(debtRatio.threshold)})`}
        value={formatPct(debtRatio.value)}
        passed={debtRatio.passed}
      />
      <Row
        label={`Cash ratio (< ${formatPct(cashRatio.threshold)})`}
        value={formatPct(cashRatio.value)}
        passed={cashRatio.passed}
      />
      {flaggedReasons.length > 0 && (
        <View style={styles.reasons}>
          {flaggedReasons.map((reason) => (
            <Text key={reason} style={styles.reasonText}>
              • {reason}
            </Text>
          ))}
        </View>
      )}
    </View>
  );
}

function Row({ label, value, passed }: { label: string; value: string; passed: boolean }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={[styles.value, { color: passed ? "#1b5e20" : "#8c1d1d" }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 10,
    padding: 16,
    gap: 12,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  label: {
    fontSize: 14,
    color: "#333",
    textTransform: "capitalize",
  },
  value: {
    fontSize: 14,
    fontWeight: "700",
  },
  reasons: {
    marginTop: 4,
    gap: 4,
  },
  reasonText: {
    fontSize: 13,
    color: "#555",
  },
});
