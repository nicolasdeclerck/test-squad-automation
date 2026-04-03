import { BlockNoteEditor } from "@blocknote/core";
import "@blocknote/core/style.css";

/**
 * Initialise un éditeur BlockNote dans le conteneur donné.
 * Le contenu HTML est synchronisé dans le champ hidden pour soumission du formulaire.
 */
async function initEditor(containerEl, hiddenInputEl, initialHTML) {
  let initialContent;

  if (initialHTML && initialHTML.trim()) {
    try {
      initialContent = await BlockNoteEditor.tryParseHTMLToBlocks(initialHTML);
    } catch {
      initialContent = undefined;
    }
  }

  const editor = BlockNoteEditor.create({ initialContent });

  const editorDiv = document.createElement("div");
  editorDiv.className = "blocknote-editor";
  containerEl.appendChild(editorDiv);

  editor.mount(editorDiv);

  async function syncHTML() {
    const html = await editor.blocksToHTMLLossy();
    hiddenInputEl.value = html;
  }

  editor.onEditorContentChange(syncHTML);

  // Synchronisation initiale
  await syncHTML();

  // S'assurer que le hidden input est à jour au submit
  const form = hiddenInputEl.closest("form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await syncHTML();
      form.submit();
    });
  }

  return editor;
}

// Expose globalement pour usage en vanilla JS
window.initBlockNoteEditor = initEditor;
