import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F5F7F8",
        surface: "#FFFFFF",
        ink: "#14181C",
        muted: "#5B6570",
        line: "#E2E6E8",
        accent: { DEFAULT: "#1F7A6C", soft: "#E4F1EE" },
        amber: { DEFAULT: "#B8863B", soft: "#FBF1E2" },
        clay: { DEFAULT: "#C1523D", soft: "#FBEAE6" },
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Inter", "Roboto", "Helvetica Neue", "Arial", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "Liberation Mono", "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.02em" }],
      },
    },
  },
  plugins: [],
};

export default config;
