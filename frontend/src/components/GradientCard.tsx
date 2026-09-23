import type { ComponentProps } from "react";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { Pressable, Text, View } from "react-native";

interface GradientCardProps {
  colors: [string, string];
  title: string;
  subtitle?: string;
  icon?: ComponentProps<typeof Ionicons>["name"];
  onPress?: () => void;
}

export function GradientCard({ colors, title, subtitle, icon, onPress }: GradientCardProps) {
  return (
    <Pressable onPress={onPress}>
      <LinearGradient
        colors={colors}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={{ borderRadius: 20 }}
        className="p-5 gap-1 min-h-[110px] justify-between"
      >
        <View className="flex-row items-center justify-between">
          <Text className="text-white text-lg font-bold flex-1" numberOfLines={1}>
            {title}
          </Text>
          {icon && <Ionicons name={icon} size={28} color="white" />}
        </View>
        {subtitle && (
          <Text className="text-white/80 text-sm" numberOfLines={1}>
            {subtitle}
          </Text>
        )}
      </LinearGradient>
    </Pressable>
  );
}
