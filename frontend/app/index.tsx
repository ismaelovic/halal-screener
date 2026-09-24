import { useRouter } from "expo-router";
import { useState } from "react";
import { FlatList, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { DisclaimerFooter } from "../src/components/DisclaimerFooter";
import { GradientCard } from "../src/components/GradientCard";
import { SearchBar } from "../src/components/SearchBar";
import { POPULAR_CARD_GRADIENTS, POPULAR_TICKERS } from "../src/config/popularTickers";
import { useDebouncedValue } from "../src/hooks/useDebouncedValue";
import { useRecentlyScreened } from "../src/hooks/useRecentlyScreened";
import { useCompanySearchQuery } from "../src/hooks/useScreeningQuery";

const SEARCH_DEBOUNCE_MS = 400;

const VERDICT_GRADIENTS: Record<string, [string, string]> = {
  halal: ["#1FBE7A", "#0E8F5C"],
  haram: ["#FF5A75", "#D6294B"],
  questionable: ["#FFB020", "#E08E00"],
};

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, SEARCH_DEBOUNCE_MS);
  const router = useRouter();
  const { data: results, isLoading, isError } = useCompanySearchQuery(debouncedQuery);
  const { recents } = useRecentlyScreened();

  const isSearching = debouncedQuery.trim().length > 0;

  return (
    <SafeAreaView className="flex-1 bg-bg" edges={["top", "bottom"]}>
      <View className="flex-1 px-5 gap-4">
        <View className="gap-1 mt-2">
          <Text className="text-white text-3xl font-extrabold">Halal Screener</Text>
          <Text className="text-muted text-sm">
            Search a stock for an instant Halal / Haram verdict.
          </Text>
        </View>

        <SearchBar value={query} onChangeText={setQuery} />

        {isSearching ? (
          <>
            {isLoading && <Text className="text-muted text-sm">Searching…</Text>}
            {isError && <Text className="text-muted text-sm">Something went wrong. Try again.</Text>}
            {!isLoading && (results?.length ?? 0) === 0 && (
              <Text className="text-muted text-sm">No matching companies found.</Text>
            )}
            <FlatList
              data={results ?? []}
              keyExtractor={(item) => `${item.ticker}.${item.exchange}`}
              contentContainerStyle={{ gap: 8, paddingBottom: 16 }}
              renderItem={({ item }) => (
                <Pressable
                  className="bg-surface rounded-2xl p-4"
                  onPress={() => router.push(`/stock/${item.ticker}.${item.exchange}`)}
                >
                  <Text className="text-white text-base font-semibold">{item.name}</Text>
                  <Text className="text-muted text-xs mt-1">
                    {item.ticker}.{item.exchange}
                  </Text>
                </Pressable>
              )}
            />
          </>
        ) : (
          <ScrollView contentContainerStyle={{ gap: 24, paddingBottom: 16 }}>
            {recents.length > 0 && (
              <View className="gap-3">
                <Text className="text-muted text-xs uppercase tracking-wide">
                  Recently screened
                </Text>
                <View className="gap-3">
                  {recents.map((entry) => (
                    <GradientCard
                      key={`${entry.ticker}.${entry.exchange}`}
                      colors={VERDICT_GRADIENTS[entry.verdict]}
                      title={entry.name}
                      subtitle={`${entry.ticker}.${entry.exchange} · ${entry.verdict}`}
                      onPress={() => router.push(`/stock/${entry.ticker}.${entry.exchange}`)}
                    />
                  ))}
                </View>
              </View>
            )}

            <View className="gap-3">
              <Text className="text-muted text-xs uppercase tracking-wide">Popular tickers</Text>
              <View className="gap-3">
                {POPULAR_TICKERS.map((item, index) => (
                  <GradientCard
                    key={`${item.ticker}.${item.exchange}`}
                    colors={POPULAR_CARD_GRADIENTS[index % POPULAR_CARD_GRADIENTS.length]}
                    title={item.name}
                    subtitle={item.subtitle}
                    onPress={() => router.push(`/stock/${item.ticker}.${item.exchange}`)}
                  />
                ))}
              </View>
            </View>
          </ScrollView>
        )}
      </View>
      <DisclaimerFooter />
    </SafeAreaView>
  );
}
