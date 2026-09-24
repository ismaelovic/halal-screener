import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { Text, View } from "react-native";

import type { Verdict } from "../api/types";

const VERDICT_COPY: Record<
  Verdict,
  { label: string; colors: [string, string]; icon: keyof typeof Ionicons.glyphMap }
> = {
  halal: { label: "Halal", colors: ["#1FBE7A", "#0E8F5C"], icon: "checkmark-circle" },
  haram: { label: "Haram", colors: ["#FF5A75", "#D6294B"], icon: "close-circle" },
  questionable: { label: "Questionable", colors: ["#FFB020", "#E08E00"], icon: "help-circle" },
};

interface VerdictCardProps {
  name: string;
  ticker: string;
  verdict: Verdict;
}

export function VerdictCard({ name, ticker, verdict }: VerdictCardProps) {
  const copy = VERDICT_COPY[verdict];

  return (
    <LinearGradient
      colors={copy.colors}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={{ borderRadius: 24 }}
      className="items-center py-8 px-6 gap-2"
    >
      <Ionicons name={copy.icon} size={72} color="white" />
      <Text className="text-white text-2xl font-extrabold mt-2">{copy.label}</Text>
      <Text className="text-white text-lg font-semibold mt-1">{name}</Text>
      <Text className="text-white/80 text-sm">{ticker}</Text>
    </LinearGradient>
  );
}
