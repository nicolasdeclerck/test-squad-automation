import { createReactBlockSpec } from "@blocknote/react";
import {
  BlockNoteSchema,
  defaultBlockSpecs,
  insertOrUpdateBlock,
} from "@blocknote/core";
import mermaid from "mermaid";
import { useEffect, useRef } from "react";

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  securityLevel: "strict",
});

export function MermaidPreview({ code, blockId }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !code || !code.trim()) return;

    const id = "mermaid-" + blockId.replace(/[^a-zA-Z0-9]/g, "");
    mermaid
      .render(id, code.trim())
      .then(({ svg }) => {
        // Safe: mermaid securityLevel "strict" sanitizes SVG output
        // (removes scripts, foreign objects, event handlers)
        if (containerRef.current) containerRef.current.innerHTML = svg;
      })
      .catch(() => {
        if (containerRef.current)
          containerRef.current.textContent = "Syntaxe mermaid invalide";
      });
  }, [code, blockId]);

  if (!code || !code.trim()) {
    return (
      <p style={{ color: "#999", fontStyle: "italic" }}>
        Écrivez votre code mermaid ci-dessus...
      </p>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{ display: "flex", justifyContent: "center", width: "100%" }}
    />
  );
}

export const MermaidBlock = createReactBlockSpec(
  {
    type: "mermaid",
    propSchema: {
      data: { default: "" },
    },
    content: "none",
  },
  {
    render: ({ block, editor }) => {
      const isEditable = editor.isEditable;
      const data = block.props.data || "";

      const onChange = (e) => {
        editor.updateBlock(block, {
          props: { ...block.props, data: e.target.value },
        });
      };

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.5em",
            border: isEditable ? "1px solid #e0e0e0" : "none",
            borderRadius: "6px",
            padding: isEditable ? "12px" : "0",
            width: "100%",
          }}
        >
          {isEditable && (
            <textarea
              value={data}
              onChange={onChange}
              placeholder={"graph TD\n    A[Début] --> B[Fin]"}
              rows={6}
              style={{
                width: "100%",
                fontFamily: "monospace",
                fontSize: "13px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                padding: "8px",
                resize: "vertical",
                outline: "none",
                backgroundColor: "#f8f9fa",
              }}
            />
          )}
          <MermaidPreview code={data} blockId={block.id} />
        </div>
      );
    },
  }
);

export const schema = BlockNoteSchema.create({
  blockSpecs: {
    ...defaultBlockSpecs,
    mermaid: MermaidBlock,
  },
});

export const insertMermaid = () => ({
  title: "Mermaid",
  group: "Autre",
  onItemClick: (editor) => {
    insertOrUpdateBlock(editor, { type: "mermaid" });
  },
  aliases: ["mermaid", "diagram", "diagramme", "chart", "graphique"],
  subtext: "Insérer un diagramme Mermaid",
});
