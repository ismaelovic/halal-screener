import { Ionicons } from "@expo/vector-icons";
import { useState } from "react";
import { TextInput, View } from "react-native";

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChangeText, placeholder }: SearchBarProps) {
  const [focused, setFocused] = useState(false);

  return (
    <View
      className={`flex-row items-center gap-2 rounded-full bg-surface px-4 h-14 border ${
        focused ? "border-white/40" : "border-white/10"
      }`}
    >
      <Ionicons name="search" size={20} color="#8A93A6" />
      <TextInput
        className="flex-1 text-white text-base"
        style={{ outlineStyle: "none" } as never}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder ?? "Search a ticker or company name…"}
        placeholderTextColor="#8A93A6"
        autoCapitalize="none"
        autoCorrect={false}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
      />
    </View>
  );
}
