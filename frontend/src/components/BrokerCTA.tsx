import { Linking, Pressable, Text, View } from "react-native";

import { BROKER_CTAS } from "../config/brokers";

export function BrokerCTA() {
  return (
    <View className="gap-2">
      <Text className="text-muted text-xs uppercase tracking-wide">Trade with</Text>
      {BROKER_CTAS.map((broker) => (
        <Pressable
          key={broker.name}
          className="bg-surface rounded-2xl p-4"
          onPress={() => Linking.openURL(broker.url)}
        >
          <Text className="text-white text-base font-bold">{broker.name}</Text>
          <Text className="text-muted text-sm mt-1">{broker.blurb}</Text>
        </Pressable>
      ))}
    </View>
  );
}
