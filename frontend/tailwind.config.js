/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  presets: [require("nativewind/preset")],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#0B0E14",
        surface: "#151923",
        surfaceAlt: "#1D2230",
        muted: "#8A93A6",
        halal: { start: "#1FBE7A", end: "#0E8F5C" },
        haram: { start: "#FF5A75", end: "#D6294B" },
        questionable: { start: "#FFB020", end: "#E08E00" },
      },
    },
  },
  plugins: [],
};
