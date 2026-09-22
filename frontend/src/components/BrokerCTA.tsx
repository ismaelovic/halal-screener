import { Linking, StyleSheet, Text, TouchableOpacity, View } from "react-native";

import { BROKER_CTAS } from "../config/brokers";

export function BrokerCTA() {
  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Trade with</Text>
      {BROKER_CTAS.map((broker) => (
        <TouchableOpacity
          key={broker.name}
          style={styles.card}
          onPress={() => Linking.openURL(broker.url)}
        >
          <Text style={styles.name}>{broker.name}</Text>
          <Text style={styles.blurb}>{broker.blurb}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 8,
  },
  heading: {
    fontSize: 13,
    color: "#777",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  card: {
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 10,
    padding: 14,
  },
  name: {
    fontSize: 15,
    fontWeight: "700",
  },
  blurb: {
    fontSize: 13,
    color: "#555",
    marginTop: 2,
  },
});
