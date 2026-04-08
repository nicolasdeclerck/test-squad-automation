import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import { useMemo } from "react";
import { schema } from "./mermaid-block";

export default function BlockNoteRenderer({ content }) {
  const blocks = useMemo(() => {
    try {
      return JSON.parse(content);
    } catch {
      return null;
    }
  }, [content]);

  const validBlocks =
    Array.isArray(blocks) && blocks.length > 0 ? blocks : undefined;

  const editor = useCreateBlockNote({
    schema,
    initialContent: validBlocks,
  });

  if (!validBlocks) {
    return <div className="whitespace-pre-line">{content}</div>;
  }

  return (
    <div className="text-gray-700 leading-relaxed">
      <BlockNoteView editor={editor} theme="light" editable={false} />
    </div>
  );
}
