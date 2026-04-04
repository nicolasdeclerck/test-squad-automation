import { BlockNoteEditor } from "https://esm.sh/@blocknote/core@0.24.2";
import { blockNoteViewCSS } from "https://esm.sh/@blocknote/core@0.24.2/style.css?raw";

(async function () {
  const container = document.getElementById("blocknote-editor");
  const hiddenInput = document.getElementById("id_content");
  if (!container || !hiddenInput) return;

  // Inject BlockNote base styles
  const style = document.createElement("style");
  style.textContent = blockNoteViewCSS;
  document.head.appendChild(style);

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
  const editorElement = editor.mount(container);

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

  // Initial sync if there's content
  if (editor.document) {
    hiddenInput.value = JSON.stringify(editor.document);
  }
})();
