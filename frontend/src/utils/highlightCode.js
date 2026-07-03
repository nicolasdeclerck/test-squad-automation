import { useEffect } from "react";

// highlight.js is loaded lazily (as its own chunk) so it only reaches the
// reader when an article that actually contains code blocks is displayed.
let hljsPromise = null;

function loadHljs() {
  if (!hljsPromise) {
    hljsPromise = import("highlight.js/lib/common").then((mod) => mod.default);
  }
  return hljsPromise;
}

// Languages BlockNote can tag but that are not part of highlight.js' "common"
// bundle are simply left un-highlighted (plain <pre>), never broken.
function languageFromClass(className) {
  const match = /(?:^|\s)language-(\S+)/.exec(className || "");
  return match ? match[1] : null;
}

/**
 * Highlights every `<pre><code class="language-…">` block found inside the
 * container once `htmlDep` changes (i.e. after the article HTML is injected).
 *
 * BlockNote highlights code live in the editor, but `blocksToFullHTML` — the
 * path used to render published articles — exports plain code with only a
 * `language-*` class. This hook restores syntax colours on the read side.
 *
 * @param {import("react").RefObject<HTMLElement>} containerRef
 * @param {string} htmlDep - the injected HTML; re-runs highlighting on change.
 */
export function useSyntaxHighlight(containerRef, htmlDep) {
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return undefined;

    const blocks = container.querySelectorAll(
      "pre code[class*='language-']",
    );
    if (blocks.length === 0) return undefined;

    let cancelled = false;
    loadHljs().then((hljs) => {
      if (cancelled) return;
      blocks.forEach((block) => {
        const lang = languageFromClass(block.className);
        // `text`/`plaintext` are intentional "no highlight" markers; unknown
        // languages are skipped so highlight.js never emits a warning.
        if (!lang || lang === "text" || lang === "plaintext") return;
        if (!hljs.getLanguage(lang)) return;
        hljs.highlightElement(block);
      });
    });

    return () => {
      cancelled = true;
    };
  }, [containerRef, htmlDep]);
}
