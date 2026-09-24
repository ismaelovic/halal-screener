import { Text, View } from "react-native";

import type { BusinessActivity, RatioBreakdown as RatioBreakdownType } from "../api/types";
import { RatioGauge } from "./RatioGauge";

interface RatioBreakdownProps {
  businessActivity: BusinessActivity;
  debtRatio: RatioBreakdownType;
  cashRatio: RatioBreakdownType;
  flaggedReasons: string[];
}

const STATUS_COPY: Record<BusinessActivity["status"], { label: string; passed: boolean }> = {
  compliant: { label: "Compliant sector", passed: true },
  non_compliant: { label: "Non-compliant sector", passed: false },
  review: { label: "Needs manual review", passed: false },
};

export function RatioBreakdown({
  businessActivity,
  debtRatio,
  cashRatio,
  flaggedReasons,
}: RatioBreakdownProps) {
  const status = STATUS_COPY[businessActivity.status];

  return (
    <View className="bg-surface rounded-3xl p-5 gap-5">
      <View
        className={`self-start rounded-full px-4 py-2 ${
          status.passed ? "bg-halal-end/30" : "bg-haram-end/30"
        }`}
      >
        <Text className={`text-sm font-semibold ${status.passed ? "text-halal-start" : "text-haram-start"}`}>
          {status.label}
        </Text>
      </View>

      <View className="flex-row justify-around">
        <RatioGauge
          label="Debt ratio"
          value={debtRatio.value}
          threshold={debtRatio.threshold}
          passed={debtRatio.passed}
        />
        <RatioGauge
          label="Cash ratio"
          value={cashRatio.value}
          threshold={cashRatio.threshold}
          passed={cashRatio.passed}
        />
      </View>

      {flaggedReasons.length > 0 && (
        <View className="gap-1">
          {flaggedReasons.map((reason) => (
            <Text key={reason} className="text-muted text-sm">
              • {reason}
            </Text>
          ))}
        </View>
      )}
    </View>
  );
}
