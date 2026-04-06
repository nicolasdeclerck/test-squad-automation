import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import {
  useCreateBlockNote,
  SuggestionMenuController,
  getDefaultReactSlashMenuItems,
} from "@blocknote/react";
import { filterSuggestionItems } from "@blocknote/core";
import { BlockNoteView } from "@blocknote/mantine";
import { schema, insertMermaid } from "./mermaid-block.js";

function BlockNoteEditorApp({ initialContent, hiddenInput }) {
  const editor = useCreateBlockNote({
    schema,
    initialContent: initialContent || undefined,
    placeholders: {
      default: "Commencez à écrire votre article...",
    },
  });

  useEffect(() => {
    if (!hiddenInput) return;

    if (initialContent) {
      hiddenInput.value = JSON.stringify(editor.document);
    }

    const unsubscribe = editor.onEditorContentChange(() => {
      hiddenInput.value = JSON.stringify(editor.document);
    });

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

  return React.createElement(
    BlockNoteView,
    { editor, theme: "light", slashMenu: false },
    React.createElement(SuggestionMenuController, {
      triggerCharacter: "/",
      getItems: async (query) =>
        filterSuggestionItems(
          [...getDefaultReactSlashMenuItems(editor), insertMermaid()],
          query
        ),
    })
  );
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
