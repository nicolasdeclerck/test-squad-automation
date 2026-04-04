import { BlockNoteEditor } from "https://esm.sh/@blocknote/core@0.24.2";

(async function () {
  const container = document.getElementById("blocknote-editor");
  const hiddenInput = document.getElementById("id_content");
  if (!container || !hiddenInput) return;

  // Parse initial content (JSON from hidden input, or empty)
  let initialContent;
  try {
    const raw = hiddenInput.value;
    if (raw) {
      initialContent = JSON.parse(raw);
    }
  } catch {
    // Plain text fallback: convert to a single paragraph block
    initialContent = undefined;
  }

  const editor = BlockNoteEditor.create({
    initialContent: initialContent || undefined,
  });

  // Mount the editor
  editor.mount(container);

  // Sync JSON to hidden input on every change
  editor.onEditorContentChange(() => {
    const blocks = editor.document;
    hiddenInput.value = JSON.stringify(blocks);
  });

  // Also sync on form submit to be safe
  const form = container.closest("form");
  if (form) {
    form.addEventListener("submit", () => {
      const blocks = editor.document;
      hiddenInput.value = JSON.stringify(blocks);
    });
  }

  // Initial sync only if content was loaded from hidden input
  if (initialContent) {
    hiddenInput.value = JSON.stringify(editor.document);
  }
})();
