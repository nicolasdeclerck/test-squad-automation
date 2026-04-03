import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "static/js",
    rollupOptions: {
      input: "frontend/editor.jsx",
      output: {
        entryFileNames: "editor.js",
        assetFileNames: "editor.[ext]",
      },
    },
  },
});
