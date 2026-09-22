import { StyleSheet, Text, View } from "react-native";

export function DisclaimerFooter({ text }: { text?: string }) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>
        {text ??
          "This is not financial advice. Screening is based on publicly available fundamentals data; verify independently before investing."}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  text: {
    fontSize: 11,
    color: "#999",
    textAlign: "center",
  },
});
