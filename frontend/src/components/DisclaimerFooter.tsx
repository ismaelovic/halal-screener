import { Text, View } from "react-native";

export function DisclaimerFooter({ text }: { text?: string }) {
  return (
    <View className="py-3 px-4">
      <Text className="text-muted text-[11px] text-center">
        {text ??
          "This is not financial advice. Screening is based on publicly available fundamentals data; verify independently before investing."}
      </Text>
    </View>
  );
}
