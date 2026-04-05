import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { BlockNoteView } from "@blocknote/mantine";
import { useCreateBlockNote } from "@blocknote/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

export default function PostForm() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(slug);
  const [title, setTitle] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(isEdit);
  const [initialContent, setInitialContent] = useState(null);
  const titleRef = useRef(null);

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
        setLoading(false);
      });
    }
  }, [slug, isEdit]);

  const editor = useCreateBlockNote({
    initialContent: initialContent || undefined,
  });

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

    const content = JSON.stringify(editor.document);

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

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="sr-only">
        {isEdit ? "Modifier l'article" : "Ajouter un article"}
      </h1>

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
            <BlockNoteView
              editor={editor}
              theme="light"
            />
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
