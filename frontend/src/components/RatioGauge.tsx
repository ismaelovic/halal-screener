import { Text, View } from "react-native";
import Svg, { Circle } from "react-native-svg";

const SIZE = 96;
const STROKE_WIDTH = 10;
const RADIUS = (SIZE - STROKE_WIDTH) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

interface RatioGaugeProps {
  label: string;
  value: number;
  threshold: number;
  passed: boolean;
}

export function RatioGauge({ label, value, threshold, passed }: RatioGaugeProps) {
  const fraction = Math.min(value / threshold, 1);
  const color = passed ? "#1FBE7A" : "#FF5A75";

  return (
    <View className="items-center gap-2">
      <View style={{ width: SIZE, height: SIZE }}>
        <Svg width={SIZE} height={SIZE}>
          <Circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={RADIUS}
            stroke="#1D2230"
            strokeWidth={STROKE_WIDTH}
            fill="none"
          />
          <Circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={RADIUS}
            stroke={color}
            strokeWidth={STROKE_WIDTH}
            strokeLinecap="round"
            fill="none"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={CIRCUMFERENCE * (1 - fraction)}
            transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
          />
        </Svg>
        <View className="absolute inset-0 items-center justify-center">
          <Text className="text-white font-bold text-base">{(value * 100).toFixed(1)}%</Text>
        </View>
      </View>
      <Text className="text-muted text-xs text-center">{label}</Text>
      <Text className="text-muted text-xs">limit {(threshold * 100).toFixed(0)}%</Text>
    </View>
  );
}
