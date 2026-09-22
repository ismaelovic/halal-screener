import { useLocalSearchParams } from "expo-router";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BrokerCTA } from "../../src/components/BrokerCTA";
import { DisclaimerFooter } from "../../src/components/DisclaimerFooter";
import { RatioBreakdown } from "../../src/components/RatioBreakdown";
import { VerdictCard } from "../../src/components/VerdictCard";
import { useScreeningQuery } from "../../src/hooks/useScreeningQuery";

export default function StockScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { data, isLoading, isError } = useScreeningQuery(ticker);

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <Text style={styles.status}>Loading…</Text>
      </SafeAreaView>
    );
  }

  if (isError || !data) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <Text style={styles.status}>Could not load a screening result for {ticker}.</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea} edges={["bottom"]}>
      <ScrollView contentContainerStyle={styles.container}>
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
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#fff",
  },
  container: {
    padding: 20,
    gap: 16,
  },
  status: {
    fontSize: 14,
    color: "#777",
    padding: 20,
  },
});
