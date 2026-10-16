import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: "#F0FDF8",
          100: "#DBFCEF",
          200: "#B8F7DE",
          300: "#7CEAC3",
          400: "#3BD3A3",
          500: "#13B785",
          600: "#09936B",
          700: "#0A7456",
          800: "#0D5B45",
          900: "#0D3B2E", // Signature Forest
          950: "#05221B",
        },
        ochre: {
          50: "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          300: "#FCD34D",
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706", // Signature Warm Ochre Accent
          700: "#B45309",
          800: "#92400E",
          900: "#78350F",
        },
        surface: {
          50: "#FFFFFF",
          100: "#FBFBF9", // Warm Off-White
          200: "#F4F4EE",
          300: "#EAEAE2",
          400: "#D6D6CC",
        },
        charcoal: {
          800: "#2D3748",
          900: "#1A201E", // Primary Typography
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Outfit", "Inter", "sans-serif"],
      },
      boxShadow: {
        subtle: "0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03)",
        card: "0 4px 6px -1px rgba(13, 59, 46, 0.05), 0 2px 4px -2px rgba(13, 59, 46, 0.05)",
        elevated: "0 10px 15px -3px rgba(13, 59, 46, 0.08), 0 4px 6px -4px rgba(13, 59, 46, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
