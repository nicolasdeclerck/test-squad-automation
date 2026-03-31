import React from "react";
import { createRoot } from "react-dom/client";
import Editor from "./editor.jsx";

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("blocknote-editor");
  if (!container) return;

  const dataEl = document.getElementById("blocknote-initial-data");
  let initialContent = [];
  if (dataEl) {
    try {
      const parsed = JSON.parse(dataEl.textContent);
      if (Array.isArray(parsed) && parsed.length > 0) {
        initialContent = parsed;
      }
    } catch {
      // ignore parse errors
    }
  }

  const contentJsonInput = document.querySelector('input[name="content_json"]');
  const contentHtmlInput = document.querySelector('input[name="content"]');

  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <Editor
        initialContent={initialContent}
        contentJsonInput={contentJsonInput}
        contentHtmlInput={contentHtmlInput}
      />
    </React.StrictMode>
  );
});
