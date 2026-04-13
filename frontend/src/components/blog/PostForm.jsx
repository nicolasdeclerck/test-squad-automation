import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { BlockNoteView } from "@blocknote/mantine";
import { useCreateBlockNote } from "@blocknote/react";
import { TagsInput } from "@mantine/core";
import { useCallback, useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useBlocker, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

const VIDEO_TYPES = ["video/mp4", "video/webm", "video/ogg"];

async function uploadFile(file) {
  const isVideo = VIDEO_TYPES.includes(file.type);
  const formData = new FormData();
  formData.append(isVideo ? "video" : "image", file);
  const endpoint = isVideo ? "/api/blog/upload-video/" : "/api/blog/upload-image/";
  const res = await api.post(endpoint, formData);
  if (res.ok) {
    return res.data.url;
  }
  const fieldErrors = isVideo ? res.errors?.video : res.errors?.image;
  throw new Error(fieldErrors?.[0] || res.errors?.detail || "Erreur lors de l'upload du fichier");
}

function BlockNoteEditor({ initialContent, editorRef, onChange }) {
  const editor = useCreateBlockNote({
    initialContent: initialContent || undefined,
    uploadFile,
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
  const [tags, setTags] = useState([]);
  const [tagSuggestions, setTagSuggestions] = useState([]);
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
  const retryCountRef = useRef(0);
  const titleValueRef = useRef("");
  const tagsValueRef = useRef([]);
  const lastSavedTitleRef = useRef("");
  const lastSavedContentRef = useRef("");
  const lastSavedTagsRef = useRef([]);

  useEffect(() => {
    if (isEdit) {
      api.get(`/api/blog/posts/${slug}/`).then((res) => {
        if (res.ok) {
          const editTitle = res.data.has_draft
            ? res.data.draft_title || res.data.title
            : res.data.title;
          const editContent = res.data.has_draft
            ? res.data.draft_content || res.data.content
            : res.data.content;
          setTitle(editTitle);
          titleValueRef.current = editTitle;
          lastSavedTitleRef.current = editTitle;
          const postTags = (res.data.tags || []).map((t) => t.name);
          setTags(postTags);
          tagsValueRef.current = postTags;
          lastSavedTagsRef.current = postTags;
          try {
            const parsed = JSON.parse(editContent);
            setInitialContent(parsed);
            lastSavedContentRef.current = editContent;
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

  const tagSearchTimerRef = useRef(null);
  const searchTags = useCallback((query) => {
    if (tagSearchTimerRef.current) {
      clearTimeout(tagSearchTimerRef.current);
    }
    if (!query.trim()) {
      setTagSuggestions([]);
      return;
    }
    tagSearchTimerRef.current = setTimeout(async () => {
      const res = await api.get(`/api/blog/tags/?search=${encodeURIComponent(query)}`);
      if (res.ok) {
        setTagSuggestions(res.data.map((t) => t.name));
      }
    }, 300);
  }, []);

  const handleTagsChange = (newTags) => {
    setTags(newTags);
    tagsValueRef.current = newTags;
    if (isEdit) {
      scheduleAutosave();
    }
  };

  const performAutosave = useCallback(async () => {
    if (!slug || isSavingRef.current) return;

    const currentTitle = titleValueRef.current;
    const currentContent = editorRef.current
      ? JSON.stringify(editorRef.current.document)
      : "";
    const currentTags = tagsValueRef.current;

    const trimmedTitle = currentTitle.trim();

    if (
      trimmedTitle === lastSavedTitleRef.current &&
      currentContent === lastSavedContentRef.current &&
      JSON.stringify(currentTags) === JSON.stringify(lastSavedTagsRef.current)
    ) {
      isDirtyRef.current = false;
      return;
    }

    isSavingRef.current = true;
    setSaveStatus("saving");

    const res = await api.patch(`/api/blog/posts/${slug}/autosave/`, {
      draft_title: trimmedTitle,
      draft_content: currentContent,
      tags: currentTags,
    });

    isSavingRef.current = false;

    if (res.ok) {
      isDirtyRef.current = false;
      retryCountRef.current = 0;
      lastSavedTitleRef.current = trimmedTitle;
      lastSavedContentRef.current = currentContent;
      lastSavedTagsRef.current = [...currentTags];
      const now = new Date();
      setLastSavedAt(
        now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
      );
      setSaveStatus("saved");
    } else {
      setSaveStatus("error");
      isDirtyRef.current = true;
      retryCountRef.current += 1;
      // Retry up to 3 times after failure, then stop until next user edit
      if (retryCountRef.current < 3) {
        autosaveTimerRef.current = setTimeout(() => {
          performAutosave();
        }, 5000);
      }
    }
  }, [slug]);

  const scheduleAutosave = useCallback(() => {
    if (!slug) return;
    isDirtyRef.current = true;
    retryCountRef.current = 0;
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }
    autosaveTimerRef.current = setTimeout(() => {
      performAutosave();
    }, 1500);
  }, [slug, performAutosave]);

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    titleValueRef.current = e.target.value;
    if (isEdit) {
      scheduleAutosave();
    }
  };

  const handleEditorChange = useCallback(() => {
    if (isEdit) {
      scheduleAutosave();
    }
  }, [isEdit, scheduleAutosave]);

  // Block in-app navigation (React Router) when dirty
  const blocker = useBlocker(
    useCallback(() => isDirtyRef.current && isEdit, [isEdit])
  );

  // Flush autosave when blocker is triggered, then proceed
  useEffect(() => {
    if (blocker.state === "blocked") {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
        autosaveTimerRef.current = null;
      }
      performAutosave().then(() => {
        blocker.proceed();
      });
    }
  }, [blocker, performAutosave]);

  // beforeunload protection for full page navigations
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

  // Flush autosave on unmount (e.g. direct URL change)
  useEffect(() => {
    return () => {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
      if (isDirtyRef.current && slug) {
        const currentTitle = titleValueRef.current.trim();
        const currentContent = editorRef.current
          ? JSON.stringify(editorRef.current.document)
          : "";
        // Fire-and-forget save on unmount
        api.patch(`/api/blog/posts/${slug}/autosave/`, {
          draft_title: currentTitle,
          draft_content: currentContent,
          tags: tagsValueRef.current,
        });
      }
    };
  }, [slug]);

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
    // In edit mode, autosave handles saving — no manual submit
    if (isEdit) return;
    setErrors({});

    if (!title.trim()) {
      setErrors({ title: ["Le titre est obligatoire."] });
      return;
    }

    const trimmedTitle = title.trim();
    const content = editorRef.current
      ? JSON.stringify(editorRef.current.document)
      : "";

    const res = await api.post("/api/blog/posts/", {
      title: trimmedTitle,
      content,
      tags,
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

        <div className="mb-5">
          <TagsInput
            label="Tags"
            placeholder="Ajouter des tags"
            value={tags}
            onChange={handleTagsChange}
            data={tagSuggestions}
            onSearchChange={searchTags}
            maxDropdownHeight={200}
            clearable
          />
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
