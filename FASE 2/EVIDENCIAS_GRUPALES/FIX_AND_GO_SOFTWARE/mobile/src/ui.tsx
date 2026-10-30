import { ReactNode } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  TextInputProps,
  View,
} from "react-native";
export const colors = {
  ink: "#122F3A",
  muted: "#60727A",
  yellow: "#FFC448",
  background: "#F4F6F5",
  border: "#DCE4E3",
  white: "#FFFFFF",
};
export function Button({
  label,
  onPress,
  busy = false,
  secondary = false,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  busy?: boolean;
  secondary?: boolean;
  disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: busy || disabled }}
      disabled={busy || disabled}
      onPress={onPress}
      style={({ pressed }) => [
        s.button,
        secondary && s.secondary,
        (pressed || busy || disabled) && { opacity: 0.55 },
      ]}
    >
      {busy ? (
        <ActivityIndicator color={colors.ink} />
      ) : (
        <Text style={s.buttonText}>{label}</Text>
      )}
    </Pressable>
  );
}
export function Field({ label, ...props }: TextInputProps & { label: string }) {
  return (
    <View style={{ gap: 7 }}>
      <Text style={s.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        placeholderTextColor="#7D8D94"
        {...props}
        style={[
          s.input,
          props.multiline && { minHeight: 100, textAlignVertical: "top" },
          props.style,
        ]}
      />
    </View>
  );
}
export function Card({ children }: { children: ReactNode }) {
  return <View style={s.card}>{children}</View>;
}
export function Chips({
  items,
  selected,
  onSelect,
}: {
  items: { id: number; name: string }[];
  selected: number[];
  onSelect: (id: number) => void;
}) {
  return (
    <View style={s.wrap}>
      {items.map((item) => (
        <Pressable
          accessibilityRole="button"
          accessibilityState={{ selected: selected.includes(item.id) }}
          key={item.id}
          onPress={() => onSelect(item.id)}
          style={[s.chip, selected.includes(item.id) && s.chipSelected]}
        >
          <Text
            style={[
              s.chipText,
              selected.includes(item.id) && { color: "white" },
            ]}
          >
            {item.name}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}
export const s = StyleSheet.create({
  page: { flex: 1, backgroundColor: colors.background },
  content: { padding: 22, gap: 18, paddingBottom: 36 },
  heading: {
    fontSize: 30,
    lineHeight: 36,
    fontWeight: "800",
    color: colors.ink,
  },
  title: { fontSize: 20, fontWeight: "700", color: colors.ink },
  body: { fontSize: 17, lineHeight: 26, color: colors.muted },
  label: { fontSize: 15, fontWeight: "600", color: colors.ink },
  card: {
    backgroundColor: colors.white,
    borderRadius: 20,
    padding: 20,
    gap: 13,
    borderWidth: 1,
    borderColor: "#E6ECE9",
  },
  input: {
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 14,
    minHeight: 50,
    fontSize: 16,
    color: colors.ink,
  },
  button: {
    backgroundColor: colors.yellow,
    minHeight: 50,
    padding: 14,
    borderRadius: 13,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonText: { fontWeight: "700", fontSize: 15, color: colors.ink },
  secondary: { backgroundColor: "#EAF0EF" },
  wrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 24,
    backgroundColor: "#E9EFED",
    minHeight: 44,
    justifyContent: "center",
  },
  chipSelected: { backgroundColor: colors.ink },
  chipText: { fontSize: 13, fontWeight: "600", color: colors.ink },
  hero: { backgroundColor: colors.ink, padding: 24, borderRadius: 24, gap: 14 },
  badge: {
    color: "#84600C",
    backgroundColor: "#FFF0CB",
    borderRadius: 8,
    padding: 8,
    alignSelf: "flex-start",
    fontWeight: "600",
    fontSize: 12,
  },
});
