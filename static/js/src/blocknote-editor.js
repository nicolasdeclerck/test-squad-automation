import { BlockNoteEditor } from "@blocknote/core";
import "@blocknote/core/style.css";

function initBlockNoteEditor(containerEl, hiddenInputEl, initialHTML) {
  let isSubmitting = false;
  const form = hiddenInputEl.closest("form");

  async function createEditor() {
    const options = {};

    if (initialHTML && initialHTML.trim()) {
      try {
        const blocks = await BlockNoteEditor.create().tryParseHTMLToBlocks(
          initialHTML
        );
        options.initialContent = blocks;
      } catch (e) {
        // Fallback: le contenu sera chargé comme paragraphe par défaut
      }
    }

    const editor = BlockNoteEditor.create(options);

    const editorDiv = document.createElement("div");
    editorDiv.className = "bn-editor-wrapper";
    containerEl.appendChild(editorDiv);
    editor.mount(editorDiv);

    editor.onChange(() => {
      hiddenInputEl.value = editor.blocksToHTMLLossy(editor.document);
    });

    if (form) {
      form.addEventListener("submit", (e) => {
        if (isSubmitting) return;
        isSubmitting = true;
        hiddenInputEl.value = editor.blocksToHTMLLossy(editor.document);
      });
    }

    return editor;
  }

  return createEditor();
}

window.initBlockNoteEditor = initBlockNoteEditor;
