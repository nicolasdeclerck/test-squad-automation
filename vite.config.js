import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, "static/js/src/blocknote-editor.js"),
      name: "BlockNoteEditor",
      fileName: "blocknote-editor",
      formats: ["iife"],
    },
    outDir: "static/js/dist",
    emptyOutDir: true,
  },
});
