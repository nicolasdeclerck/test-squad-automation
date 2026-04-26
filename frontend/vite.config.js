/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8001",
      "/media": "http://localhost:8001",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.js"],
    css: false,
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: ["src/**/*.{js,jsx}"],
      exclude: [
        "src/**/*.test.{js,jsx}",
        "src/main.jsx",
        "src/App.jsx",
      ],
      // Target: 80% (parity with the backend, see CLAUDE.md > Tests).
      // Thresholds are intentionally NOT enforced yet — flip them on once
      // the suite catches up on src/api, src/contexts and the main
      // components.
      // thresholds: { lines: 80, functions: 80, branches: 80, statements: 80 },
    },
  },
});
