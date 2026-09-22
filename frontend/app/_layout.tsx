import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";

const queryClient = new QueryClient();

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: "#fff" },
            headerTitleStyle: { fontWeight: "700" },
          }}
        >
          <Stack.Screen name="index" options={{ title: "Halal Screener" }} />
          <Stack.Screen name="stock/[ticker]" options={{ title: "Screening result" }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
