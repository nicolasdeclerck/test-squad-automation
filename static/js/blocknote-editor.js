import React from "react";
import { createRoot } from "react-dom/client";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";

function BlockNoteEditorApp({ initialContent, hiddenInput }) {
  const editor = useCreateBlockNote({
    initialContent: initialContent || undefined,
    placeholders: {
      default: "Commencez \u00e0 \u00e9crire votre article...",
    },
  });

  React.useEffect(() => {
    if (!hiddenInput) return;

    // Initial sync
    if (initialContent) {
      hiddenInput.value = JSON.stringify(editor.document);
    }

    // Sync on every change
    const unsubscribe = editor.onEditorContentChange(() => {
      hiddenInput.value = JSON.stringify(editor.document);
    });

    // Sync on form submit
    const form = hiddenInput.closest("form");
    const handleSubmit = () => {
      hiddenInput.value = JSON.stringify(editor.document);
    };
    if (form) form.addEventListener("submit", handleSubmit);

    return () => {
      unsubscribe?.();
      if (form) form.removeEventListener("submit", handleSubmit);
    };
  }, [editor, hiddenInput, initialContent]);

  return React.createElement(BlockNoteView, { editor, theme: "light" });
}

(function () {
  const container = document.getElementById("blocknote-editor");
  const hiddenInput = document.getElementById("id_content");
  if (!container || !hiddenInput) return;

  let initialContent;
  try {
    const raw = hiddenInput.value;
    if (raw) {
      initialContent = JSON.parse(raw);
    }
  } catch {
    initialContent = undefined;
  }

  const root = createRoot(container);
  root.render(
    React.createElement(BlockNoteEditorApp, { initialContent, hiddenInput })
  );
})();
