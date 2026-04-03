import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { BlockNoteView } from "@blocknote/mantine";
import { useCreateBlockNote } from "@blocknote/react";
import "@blocknote/mantine/style.css";

function BlockNoteEditor({ initialContent, hiddenInputName, readOnly }) {
  const editor = useCreateBlockNote({
    initialContent: initialContent || undefined,
  });

  useEffect(() => {
    if (readOnly) return;

    const hiddenInput = document.querySelector(
      `input[name="${hiddenInputName}"]`
    );
    if (!hiddenInput) return;

    const unsubscribe = editor.onChange(() => {
      hiddenInput.value = JSON.stringify(editor.document);
    });

    // Set initial value
    hiddenInput.value = JSON.stringify(editor.document);

    return () => {
      if (typeof unsubscribe === "function") {
        unsubscribe();
      }
    };
  }, [editor, hiddenInputName, readOnly]);

  return <BlockNoteView editor={editor} editable={!readOnly} theme="light" />;
}

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("blocknote-editor");
  if (!container) return;

  const readOnly = container.dataset.readonly === "true";
  const hiddenInputName = container.dataset.fieldName || "content";

  let initialContent = null;
  const raw = container.dataset.initialContent;
  if (raw) {
    try {
      initialContent = JSON.parse(raw);
    } catch {
      initialContent = null;
    }
  }

  const root = createRoot(container);
  root.render(
    <BlockNoteEditor
      initialContent={initialContent}
      hiddenInputName={hiddenInputName}
      readOnly={readOnly}
    />
  );
});
