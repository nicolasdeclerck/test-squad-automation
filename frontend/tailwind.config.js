/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
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
          ink: "#111111",
          ink2: "#1f1f1f",
          text: "#2a2a2a",
          dim: "#6b6b6b",
          dim2: "#9a9a9a",
          rule: "#e7e5e0",
          rule2: "#f0efeb",
          paper: "#fbfaf7",
          accent: "#b54b1a",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
