import React, { useMemo } from "react";
import { createRoot } from "react-dom/client";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import { schema } from "./mermaid-block.js";

function BlockNoteRendererApp({ content }) {
  const blocks = useMemo(() => {
    try {
      return JSON.parse(content);
    } catch {
      return null;
    }
  }, [content]);

  const editor = useCreateBlockNote({
    schema,
    initialContent: blocks || undefined,
  });

  if (!blocks) {
    return React.createElement(
      "div",
      { className: "whitespace-pre-line" },
      content
    );
  }

  return React.createElement(BlockNoteView, {
    editor,
    editable: false,
    theme: "light",
  });
}

(function () {
  const container = document.getElementById("blocknote-content");
  if (!container) return;

  const dataScript = document.getElementById("blocknote-data");
  const content = dataScript ? dataScript.textContent : container.getAttribute("data-content");
  if (!content) return;

  const root = createRoot(container);
  root.render(React.createElement(BlockNoteRendererApp, { content }));
})();
