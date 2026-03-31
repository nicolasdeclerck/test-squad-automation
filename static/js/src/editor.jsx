import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";

import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import { useCallback, useEffect, useRef } from "react";

export default function Editor({ initialContent, contentJsonInput, contentHtmlInput }) {
  const editor = useCreateBlockNote({
    initialContent: initialContent && initialContent.length > 0 ? initialContent : undefined,
  });

  const contentJsonRef = useRef(contentJsonInput);
  const contentHtmlRef = useRef(contentHtmlInput);

  const syncToHiddenFields = useCallback(async () => {
    const blocks = editor.document;
    const jsonStr = JSON.stringify(blocks);

    if (contentJsonRef.current) {
      contentJsonRef.current.value = jsonStr;
    }

    if (contentHtmlRef.current) {
      const html = await editor.blocksToHTMLLossy(blocks);
      contentHtmlRef.current.value = html;
    }
  }, [editor]);

  useEffect(() => {
    syncToHiddenFields();
  }, [syncToHiddenFields]);

  const handleChange = useCallback(() => {
    syncToHiddenFields();
  }, [syncToHiddenFields]);

  return (
    <BlockNoteView
      editor={editor}
      onChange={handleChange}
      theme="light"
    />
  );
}
