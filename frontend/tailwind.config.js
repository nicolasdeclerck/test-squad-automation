/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: [
          "'Source Serif 4'",
          "'Source Serif Pro'",
          "Georgia",
          "serif",
        ],
      },
      colors: {
        editorial: {
          ink: "rgb(var(--color-editorial-ink) / <alpha-value>)",
          ink2: "rgb(var(--color-editorial-ink2) / <alpha-value>)",
          text: "rgb(var(--color-editorial-text) / <alpha-value>)",
          dim: "rgb(var(--color-editorial-dim) / <alpha-value>)",
          dim2: "rgb(var(--color-editorial-dim2) / <alpha-value>)",
          rule: "rgb(var(--color-editorial-rule) / <alpha-value>)",
          rule2: "rgb(var(--color-editorial-rule2) / <alpha-value>)",
          paper: "rgb(var(--color-editorial-paper) / <alpha-value>)",
          card: "rgb(var(--color-editorial-card) / <alpha-value>)",
          accent: "rgb(var(--color-editorial-accent) / <alpha-value>)",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
