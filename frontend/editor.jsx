import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import "@blocknote/mantine/style.css";

function Editor({ initialContent, readonly, hiddenInputName }) {
  const editor = useCreateBlockNote({
    initialContent:
      initialContent && initialContent.length > 0
        ? initialContent
        : undefined,
  });

  useEffect(() => {
    if (readonly || !hiddenInputName) return;

    const hiddenInput = document.querySelector(
      `input[name="${hiddenInputName}"]`
    );
    if (!hiddenInput) return;

    // Set initial value
    hiddenInput.value = JSON.stringify(editor.document);

    // Sync on every change
    editor.onEditorContentChange(() => {
      hiddenInput.value = JSON.stringify(editor.document);
    });
  }, [editor, readonly, hiddenInputName]);

  return <BlockNoteView editor={editor} editable={!readonly} theme="light" />;
}

document.querySelectorAll("[data-blocknote-editor]").forEach((container) => {
  const initialContentStr = container.getAttribute("data-initial-content");
  const readonly = container.hasAttribute("data-readonly");
  const hiddenInputName =
    container.getAttribute("data-hidden-input") || "content";

  let initialContent = [];
  if (initialContentStr) {
    try {
      initialContent = JSON.parse(initialContentStr);
    } catch (e) {
      console.warn("BlockNote: failed to parse initial content", e);
    }
  }

  const root = createRoot(container);
  root.render(
    <Editor
      initialContent={initialContent}
      readonly={readonly}
      hiddenInputName={hiddenInputName}
    />
  );
});
