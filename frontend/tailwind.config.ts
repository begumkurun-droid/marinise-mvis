import type { Config } from "tailwindcss";

// Section 16 kurumsal kimlik: Lacivert, Turuncu, Beyaz, Açık gri.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        marinise: {
          navy: "#0B2545",
          navyLight: "#13335E",
          orange: "#F4792E",
          gray: "#F2F4F7",
          white: "#FFFFFF",
        },
      },
    },
  },
  plugins: [],
};

export default config;
