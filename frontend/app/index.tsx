import { useRouter } from "expo-router";
import { useState } from "react";
import { FlatList, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { DisclaimerFooter } from "../src/components/DisclaimerFooter";
import { SearchBar } from "../src/components/SearchBar";
import { useDebouncedValue } from "../src/hooks/useDebouncedValue";
import { useCompanySearchQuery } from "../src/hooks/useScreeningQuery";

const SEARCH_DEBOUNCE_MS = 400;

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, SEARCH_DEBOUNCE_MS);
  const router = useRouter();
  const { data: results, isLoading, isError } = useCompanySearchQuery(debouncedQuery);

  return (
    <SafeAreaView style={styles.safeArea} edges={["bottom"]}>
      <View style={styles.container}>
        <Text style={styles.title}>Halal Screener</Text>
        <Text style={styles.subtitle}>Search a stock for an instant Halal / Haram verdict.</Text>
        <SearchBar value={query} onChangeText={setQuery} />

        {isLoading && <Text style={styles.status}>Searching…</Text>}
        {isError && <Text style={styles.status}>Something went wrong. Try again.</Text>}
        {!isLoading && debouncedQuery.trim().length > 0 && (results?.length ?? 0) === 0 && (
          <Text style={styles.status}>No matching companies found.</Text>
        )}


        <FlatList
          data={results ?? []}
          keyExtractor={(item) => `${item.ticker}.${item.exchange}`}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.resultRow}
              onPress={() => router.push(`/stock/${item.ticker}.${item.exchange}`)}
            >
              <Text style={styles.resultName}>{item.name}</Text>
              <Text style={styles.resultTicker}>
                {item.ticker}.{item.exchange}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>
      <DisclaimerFooter />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#fff",
  },
  container: {
    flex: 1,
    padding: 20,
    gap: 12,
  },
  title: {
    fontSize: 26,
    fontWeight: "800",
  },
  subtitle: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
  },
  status: {
    fontSize: 14,
    color: "#777",
    marginTop: 8,
  },
  list: {
    gap: 8,
    paddingTop: 8,
  },
  resultRow: {
    borderWidth: 1,
    borderColor: "#eee",
    borderRadius: 8,
    padding: 12,
  },
  resultName: {
    fontSize: 15,
    fontWeight: "600",
  },
  resultTicker: {
    fontSize: 12,
    color: "#888",
    marginTop: 2,
  },
});
