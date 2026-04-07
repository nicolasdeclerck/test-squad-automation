import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { useCreateBlockNote } from "@blocknote/react";
import DOMPurify from "dompurify";
import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api/client";

function BlockNoteRenderer({ content }) {
  const blocks = useMemo(() => {
    try {
      return JSON.parse(content);
    } catch {
      return null;
    }
  }, [content]);

  const editor = useCreateBlockNote({
    initialContent: blocks || undefined,
  });

  const [html, setHtml] = useState("");

  useEffect(() => {
    if (editor && blocks) {
      editor.blocksToFullHTML(editor.document).then((rawHtml) => {
        setHtml(DOMPurify.sanitize(rawHtml));
      });
    }
  }, [editor, blocks]);

  if (!blocks) {
    return <div className="whitespace-pre-line">{content}</div>;
  }

  return (
    <div
      className="text-gray-700 leading-relaxed"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

export default function VersionDetail() {
  const { slug, versionNumber } = useParams();
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get(`/api/blog/posts/${slug}/versions/${versionNumber}/`)
      .then((res) => {
        if (res.ok) {
          setVersion(res.data);
        } else {
          setError("Version introuvable.");
        }
        setLoading(false);
      });
  }, [slug, versionNumber]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-red-600 text-center">{error}</p>
        <div className="mt-6 text-center">
          <Link
            to={`/articles/${slug}/versions`}
            className="text-sm text-gray-500 hover:text-black transition-colors"
          >
            &larr; Retour à l'historique
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>
          Version {version.version_number} — {version.title}
        </title>
      </Helmet>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-black text-white text-sm font-medium shrink-0">
            {version.version_number}
          </span>
          <h1 className="text-3xl font-bold text-gray-900">{version.title}</h1>
        </div>
        <p className="text-sm text-gray-500">
          Publiée le{" "}
          {new Date(version.published_at).toLocaleDateString("fr-FR", {
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>

      <BlockNoteRenderer content={version.content} />

      <div className="mt-10 flex gap-4">
        <Link
          to={`/articles/${slug}/versions`}
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          &larr; Retour à l'historique
        </Link>
        <Link
          to={`/articles/${slug}`}
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          Voir l'article actuel
        </Link>
      </div>
    </div>
  );
}
