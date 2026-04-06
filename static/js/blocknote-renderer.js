import React, { useEffect, useState, useRef, useMemo } from "react";
import { createRoot } from "react-dom/client";
import {
  useCreateBlockNote,
  createReactBlockSpec,
} from "@blocknote/react";
import { BlockNoteSchema, defaultBlockSpecs } from "@blocknote/core";
import { BlockNoteView } from "@blocknote/mantine";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  securityLevel: "strict",
});

function MermaidPreview({ code, blockId }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !code || !code.trim()) return;

    const id = "mermaid-" + blockId.replace(/[^a-zA-Z0-9]/g, "");
    mermaid
      .render(id, code.trim())
      .then(({ svg }) => {
        if (containerRef.current) containerRef.current.innerHTML = svg;
      })
      .catch(() => {
        if (containerRef.current)
          containerRef.current.textContent = "Diagramme invalide";
      });
  }, [code, blockId]);

  if (!code || !code.trim()) return null;

  return React.createElement("div", {
    ref: containerRef,
    style: { display: "flex", justifyContent: "center", width: "100%" },
  });
}

const MermaidBlock = createReactBlockSpec(
  {
    type: "mermaid",
    propSchema: {
      data: { default: "" },
    },
    content: "none",
  },
  {
    render: ({ block }) => {
      const data = block.props.data || "";
      return React.createElement(
        "div",
        { style: { width: "100%", padding: "8px 0" } },
        React.createElement(MermaidPreview, { code: data, blockId: block.id })
      );
    },
  }
);

const schema = BlockNoteSchema.create({
  blockSpecs: {
    ...defaultBlockSpecs,
    mermaid: MermaidBlock,
  },
});

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

  const content = container.getAttribute("data-content");
  if (!content) return;

  const root = createRoot(container);
  root.render(React.createElement(BlockNoteRendererApp, { content }));
})();
