import { Ionicons } from "@expo/vector-icons";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BrokerCTA } from "../../src/components/BrokerCTA";
import { DisclaimerFooter } from "../../src/components/DisclaimerFooter";
import { RatioBreakdown } from "../../src/components/RatioBreakdown";
import { VerdictCard } from "../../src/components/VerdictCard";
import { useRecentlyScreened } from "../../src/hooks/useRecentlyScreened";
import { useScreeningQuery } from "../../src/hooks/useScreeningQuery";

export default function StockScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const router = useRouter();
  const { data, isLoading, isError } = useScreeningQuery(ticker);
  const { addRecent } = useRecentlyScreened();

  useEffect(() => {
    if (data) {
      const [tickerPart, exchangePart] = ticker.split(".");
      addRecent({
        ticker: tickerPart,
        exchange: exchangePart,
        name: data.name,
        verdict: data.verdict,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  return (
    <SafeAreaView className="flex-1 bg-bg" edges={["top", "bottom"]}>
      <View className="flex-row items-center px-4 py-3 gap-2">
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Ionicons name="chevron-back" size={26} color="white" />
        </Pressable>
        <Text className="text-white text-base font-semibold">{ticker}</Text>
      </View>

      {isLoading && (
        <View className="flex-1 items-center justify-center">
          <Text className="text-muted text-sm">Loading…</Text>
        </View>
      )}

      {!isLoading && (isError || !data) && (
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-muted text-sm text-center">
            Could not load a screening result for {ticker}.
          </Text>
        </View>
      )}

      {!isLoading && data && (
        <>
          <ScrollView contentContainerStyle={{ padding: 20, gap: 16 }}>
            <VerdictCard name={data.name} ticker={data.ticker} verdict={data.verdict} />
            <RatioBreakdown
              businessActivity={data.business_activity}
              debtRatio={data.debt_ratio}
              cashRatio={data.cash_ratio}
              flaggedReasons={data.flagged_reasons}
            />
            <BrokerCTA />
          </ScrollView>
          <DisclaimerFooter text={data.disclaimer} />
        </>
      )}
    </SafeAreaView>
  );
}
