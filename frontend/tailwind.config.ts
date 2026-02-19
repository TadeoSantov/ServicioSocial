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
        primary: "#1a1a2e",
        accent: "#4361ee",
        "accent-light": "#eef1ff",
        surface: "#ffffff",
        "surface-alt": "#f8f9fc",
        border: "#e2e5f1",
        "text-primary": "#1a1a2e",
        "text-muted": "#6b7280",
        success: "#059669",
        warning: "#d97706",
        danger: "#dc2626",
      },
    },
  },
  plugins: [],
};

export default config;
