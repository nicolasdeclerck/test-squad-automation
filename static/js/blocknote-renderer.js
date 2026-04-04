import { BlockNoteEditor } from "https://esm.sh/@blocknote/core@0.24.2";

(async function () {
  const container = document.getElementById("blocknote-content");
  if (!container) return;

  const rawContent = container.dataset.content;
  if (!rawContent) return;

  let blocks;
  try {
    blocks = JSON.parse(rawContent);
  } catch {
    // Not valid JSON — display as plain text (legacy content)
    container.style.whiteSpace = "pre-line";
    container.textContent = rawContent;
    return;
  }

  // Convert BlockNote JSON blocks to HTML
  const editor = BlockNoteEditor.create();
  const html = await editor.blocksToFullHTML(blocks);
  container.innerHTML = html;
})();
