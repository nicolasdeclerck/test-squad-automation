import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { BlockNoteView } from "@blocknote/mantine";
import {
  useCreateBlockNote,
  createReactBlockSpec,
  SuggestionMenuController,
  getDefaultReactSlashMenuItems,
} from "@blocknote/react";
import {
  BlockNoteSchema,
  defaultBlockSpecs,
  insertOrUpdateBlock,
  filterSuggestionItems,
} from "@blocknote/core";
import mermaid from "mermaid";
import { useCallback, useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  securityLevel: "strict",
});

function MermaidPreview({ code, blockId }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !code || !code.trim()) return;

    const id = "mermaid-" + blockId.replace(/[^a-zA-Z0-9]/g, "");
    mermaid
      .render(id, code.trim())
      .then(({ svg }) => {
        if (containerRef.current) containerRef.current.innerHTML = svg;
      })
      .catch(() => {
        if (containerRef.current)
          containerRef.current.textContent = "Syntaxe mermaid invalide";
      });
  }, [code, blockId]);

  if (!code || !code.trim()) {
    return (
      <p style={{ color: "#999", fontStyle: "italic" }}>
        Écrivez votre code mermaid ci-dessus...
      </p>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{ display: "flex", justifyContent: "center", width: "100%" }}
    />
  );
}

const MermaidBlock = createReactBlockSpec(
  {
    type: "mermaid",
    propSchema: {
      data: { default: "" },
    },
    content: "none",
  },
  {
    render: ({ block, editor }) => {
      const isEditable = editor.isEditable;
      const data = block.props.data || "";

      const onChange = useCallback(
        (e) => {
          editor.updateBlock(block, {
            props: { ...block.props, data: e.target.value },
          });
        },
        [editor, block]
      );

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.5em",
            border: isEditable ? "1px solid #e0e0e0" : "none",
            borderRadius: "6px",
            padding: isEditable ? "12px" : "0",
            width: "100%",
          }}
        >
          {isEditable && (
            <textarea
              value={data}
              onChange={onChange}
              placeholder={"graph TD\n    A[Début] --> B[Fin]"}
              rows={6}
              style={{
                width: "100%",
                fontFamily: "monospace",
                fontSize: "13px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                padding: "8px",
                resize: "vertical",
                outline: "none",
                backgroundColor: "#f8f9fa",
              }}
            />
          )}
          <MermaidPreview code={data} blockId={block.id} />
        </div>
      );
    },
  }
);

const schema = BlockNoteSchema.create({
  blockSpecs: {
    ...defaultBlockSpecs,
    mermaid: MermaidBlock,
  },
});

const insertMermaid = () => ({
  title: "Mermaid",
  group: "Autre",
  onItemClick: (editor) => {
    insertOrUpdateBlock(editor, { type: "mermaid" });
  },
  aliases: ["mermaid", "diagram", "diagramme", "chart", "graphique"],
  subtext: "Insérer un diagramme Mermaid",
});

function BlockNoteEditor({ initialContent, editorRef }) {
  const editor = useCreateBlockNote({
    schema,
    initialContent: initialContent || undefined,
  });

  useEffect(() => {
    editorRef.current = editor;
  }, [editor, editorRef]);

  return (
    <BlockNoteView editor={editor} theme="light" slashMenu={false}>
      <SuggestionMenuController
        triggerCharacter="/"
        getItems={async (query) =>
          filterSuggestionItems(
            [...getDefaultReactSlashMenuItems(editor), insertMermaid()],
            query
          )
        }
      />
    </BlockNoteView>
  );
}

export default function PostForm() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(slug);
  const [title, setTitle] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(isEdit);
  const [initialContent, setInitialContent] = useState(undefined);
  const [contentReady, setContentReady] = useState(!isEdit);
  const titleRef = useRef(null);
  const editorRef = useRef(null);

  useEffect(() => {
    if (isEdit) {
      api.get(`/api/blog/posts/${slug}/`).then((res) => {
        if (res.ok) {
          setTitle(res.data.title);
          try {
            setInitialContent(JSON.parse(res.data.content));
          } catch {
            setInitialContent(undefined);
          }
        }
        setContentReady(true);
        setLoading(false);
      });
    }
  }, [slug, isEdit]);

  const autoResize = () => {
    if (titleRef.current) {
      titleRef.current.style.height = "auto";
      titleRef.current.style.height = titleRef.current.scrollHeight + "px";
    }
  };

  useEffect(() => {
    autoResize();
  }, [title]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    const content = editorRef.current
      ? JSON.stringify(editorRef.current.document)
      : "";

    let res;
    if (isEdit) {
      res = await api.patch(`/api/blog/posts/${slug}/`, { title, content });
    } else {
      res = await api.post("/api/blog/posts/", { title, content });
    }

    if (res.ok) {
      navigate(`/articles/${res.data.slug}`);
    } else if (res.errors) {
      setErrors(res.errors);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  const pageTitle = isEdit ? "Modifier l'article" : "Ajouter un article";

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <Helmet>
        <title>{pageTitle}</title>
        <meta name="description" content={pageTitle} />
      </Helmet>

      <h1 className="sr-only">{pageTitle}</h1>

      {errors.non_field_errors && (
        <div className="mb-6 p-3 border border-red-200 rounded">
          {errors.non_field_errors.map((err, i) => (
            <p key={i} className="form-error">
              {err}
            </p>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-5">
          <label htmlFor="title" className="sr-only">
            Titre
          </label>
          <textarea
            ref={titleRef}
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre de l'article"
            required
            rows={1}
            maxLength={200}
            onInput={autoResize}
            className={`w-full text-2xl sm:text-3xl font-bold text-gray-900 border-0 outline-none focus:ring-0 bg-transparent placeholder-gray-300 p-0 resize-none overflow-hidden break-words${
              errors.title ? " border-b-2 border-red-500" : ""
            }`}
          />
          {errors.title &&
            errors.title.map((err, i) => (
              <p key={i} className="form-error mt-1">
                {err}
              </p>
            ))}
        </div>

        <div className="mb-6">
          <label className="sr-only">Contenu</label>
          <div
            style={{ minHeight: "300px" }}
            className={errors.content ? "border border-red-500" : ""}
          >
            {contentReady && (
              <BlockNoteEditor
                initialContent={initialContent}
                editorRef={editorRef}
              />
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Raccourcis : <kbd>Ctrl+B</kbd> gras, <kbd>Ctrl+I</kbd> italique,{" "}
            <kbd>/</kbd> pour les blocs (titres, listes, mermaid, etc.)
          </p>
          {errors.content &&
            errors.content.map((err, i) => (
              <p key={i} className="form-error mt-1">
                {err}
              </p>
            ))}
        </div>

        <button type="submit" className="btn-primary w-full py-3">
          {isEdit ? "Modifier" : "Publier"}
        </button>
      </form>

      <div className="mt-6 text-center">
        <Link
          to="/"
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          Retour
        </Link>
      </div>
    </div>
  );
}
