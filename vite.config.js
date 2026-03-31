import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  root: ".",
  base: "/static/",
  build: {
    outDir: "static/js/dist",
    manifest: "manifest.json",
    rollupOptions: {
      input: "static/js/src/index.jsx",
    },
  },
  server: {
    port: 5173,
    origin: "http://localhost:5173",
  },
});
