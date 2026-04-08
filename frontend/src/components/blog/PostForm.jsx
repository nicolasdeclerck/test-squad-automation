import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { BlockNoteView } from "@blocknote/mantine";
import { useCreateBlockNote } from "@blocknote/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

function BlockNoteEditor({ initialContent, editorRef, onChange }) {
  const editor = useCreateBlockNote({
    initialContent: initialContent || undefined,
  });

  useEffect(() => {
    editorRef.current = editor;
  }, [editor, editorRef]);

  return (
    <BlockNoteView
      editor={editor}
      theme="light"
      onChange={onChange}
    />
  );
}

function SaveStatusIndicator({ saveStatus, lastSavedAt }) {
  if (saveStatus === "idle") return null;

  const statusConfig = {
    saving: { text: "Sauvegarde en cours...", className: "text-gray-400" },
    saved: {
      text: lastSavedAt
        ? `Brouillon sauvegardé à ${lastSavedAt}`
        : "Brouillon sauvegardé",
      className: "text-green-600",
    },
    error: { text: "Erreur de sauvegarde", className: "text-red-500" },
  };

  const config = statusConfig[saveStatus];
  if (!config) return null;

  return (
    <p className={`text-xs ${config.className} mb-4`}>
      {config.text}
    </p>
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
  const [saveStatus, setSaveStatus] = useState("idle");
  const [lastSavedAt, setLastSavedAt] = useState(null);
  const titleRef = useRef(null);
  const editorRef = useRef(null);
  const autosaveTimerRef = useRef(null);
  const isDirtyRef = useRef(false);
  const isSavingRef = useRef(false);
  const lastSavedTitleRef = useRef("");
  const lastSavedContentRef = useRef("");

  useEffect(() => {
    if (isEdit) {
      api.get(`/api/blog/posts/${slug}/`).then((res) => {
        if (res.ok) {
          setTitle(res.data.title);
          lastSavedTitleRef.current = res.data.title;
          try {
            const parsed = JSON.parse(res.data.content);
            setInitialContent(parsed);
            lastSavedContentRef.current = res.data.content;
          } catch {
            setInitialContent(undefined);
            lastSavedContentRef.current = "";
          }
        }
        setContentReady(true);
        setLoading(false);
      });
    }
  }, [slug, isEdit]);

  const performAutosave = useCallback(async () => {
    if (!slug || isSavingRef.current) return;

    const currentTitle = document.getElementById("title")?.value || "";
    const currentContent = editorRef.current
      ? JSON.stringify(editorRef.current.document)
      : "";

    if (
      currentTitle === lastSavedTitleRef.current &&
      currentContent === lastSavedContentRef.current
    ) {
      isDirtyRef.current = false;
      return;
    }

    isSavingRef.current = true;
    setSaveStatus("saving");

    const res = await api.patch(`/api/blog/posts/${slug}/autosave/`, {
      draft_title: currentTitle.trim(),
      draft_content: currentContent,
    });

    isSavingRef.current = false;

    if (res.ok) {
      isDirtyRef.current = false;
      lastSavedTitleRef.current = currentTitle;
      lastSavedContentRef.current = currentContent;
      const now = new Date();
      setLastSavedAt(
        now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
      );
      setSaveStatus("saved");
    } else {
      setSaveStatus("error");
    }
  }, [slug]);

  const scheduleAutosave = useCallback(() => {
    if (!slug) return;
    isDirtyRef.current = true;
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }
    autosaveTimerRef.current = setTimeout(() => {
      performAutosave();
    }, 1500);
  }, [slug, performAutosave]);

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    if (isEdit) {
      scheduleAutosave();
    }
  };

  const handleEditorChange = useCallback(() => {
    if (isEdit) {
      scheduleAutosave();
    }
  }, [isEdit, scheduleAutosave]);

  // beforeunload protection
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (isDirtyRef.current) {
        e.preventDefault();
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  // Cleanup autosave timer on unmount
  useEffect(() => {
    return () => {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
    };
  }, []);

  const autoResize = () => {
    if (titleRef.current) {
      titleRef.current.style.height = "auto";
      titleRef.current.style.height = titleRef.current.scrollHeight + "px";
    }
  };

  useEffect(() => {
    autoResize();
  }, [title]);

  const handleSubmit = async (e, { publish = false } = {}) => {
    e.preventDefault();
    setErrors({});

    if (!title.trim()) {
      setErrors({ title: ["Le titre est obligatoire."] });
      return;
    }

    const trimmedTitle = title.trim();
    const content = editorRef.current
      ? JSON.stringify(editorRef.current.document)
      : "";

    // New article: create via POST then redirect to edit mode (autosave activates)
    const res = await api.post("/api/blog/posts/", {
      title: trimmedTitle,
      content,
    });

    if (res.ok) {
      if (publish) {
        const publishRes = await api.post(
          `/api/blog/posts/${res.data.slug}/publish/`
        );
        if (publishRes.ok) {
          navigate(`/articles/${publishRes.data.slug}`);
          return;
        }
        if (publishRes.errors) {
          setErrors(publishRes.errors);
        } else if (publishRes.data?.error) {
          setErrors({ non_field_errors: [publishRes.data.error] });
        }
        return;
      }
      // After first save, redirect to edit mode where autosave is active
      navigate(`/articles/${res.data.slug}/modifier`);
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
            onChange={handleTitleChange}
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

        {isEdit && <SaveStatusIndicator saveStatus={saveStatus} lastSavedAt={lastSavedAt} />}

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
                onChange={handleEditorChange}
              />
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Raccourcis : <kbd>Ctrl+B</kbd> gras, <kbd>Ctrl+I</kbd> italique,{" "}
            <kbd>/</kbd> pour les blocs (titres, listes, etc.)
          </p>
          {errors.content &&
            errors.content.map((err, i) => (
              <p key={i} className="form-error mt-1">
                {err}
              </p>
            ))}
        </div>

        {!isEdit && (
          <div className="flex gap-3">
            <button
              type="button"
              onClick={(e) => handleSubmit(e, { publish: false })}
              className="btn-secondary flex-1 py-3"
            >
              Enregistrer en brouillon
            </button>
            <button
              type="button"
              onClick={(e) => handleSubmit(e, { publish: true })}
              className="btn-primary flex-1 py-3"
            >
              Publier
            </button>
          </div>
        )}
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
