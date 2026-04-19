import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { useCreateBlockNote } from "@blocknote/react";
import { Button, Modal } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import DOMPurify from "dompurify";
import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

function BlockNoteRenderer({ content }) {
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
    initialContent: validBlocks,
  });

  const [html, setHtml] = useState("");

  useEffect(() => {
    if (editor && validBlocks) {
      editor.blocksToFullHTML(editor.document).then((rawHtml) => {
        setHtml(DOMPurify.sanitize(rawHtml));
      }).catch(() => {});
    }
  }, [editor, validBlocks]);

  if (!validBlocks) {
    return <div className="whitespace-pre-line">{content}</div>;
  }

  return (
    <div
      className="article-prose"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

export default function VersionDetail() {
  const { slug, versionNumber } = useParams();
  const navigate = useNavigate();
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [restoreModalOpen, setRestoreModalOpen] = useState(false);
  const [restoring, setRestoring] = useState(false);

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

  const handleRestore = async () => {
    setRestoring(true);
    const res = await api.post(
      `/api/blog/posts/${slug}/versions/${versionNumber}/restore/`
    );
    setRestoring(false);
    if (res.ok) {
      setRestoreModalOpen(false);
      notifications.show({
        title: "Version restaurée",
        message: `Le contenu de la version ${versionNumber} a été restauré comme brouillon.`,
        color: "green",
      });
      navigate(`/articles/${slug}/modifier`);
    } else {
      setRestoreModalOpen(false);
      notifications.show({
        title: "Erreur",
        message: "Impossible de restaurer cette version.",
        color: "red",
      });
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-editorial-dim text-center">Chargement...</p>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-red-600 dark:text-red-400 text-center">{error}</p>
        <div className="mt-6 text-center">
          <Link
            to={`/articles/${slug}/versions`}
            className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
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
        <title>{`Version ${version.version_number} — ${version.title}`}</title>
      </Helmet>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-editorial-ink text-editorial-paper text-sm font-medium shrink-0">
            {version.version_number}
          </span>
          <h1 className="text-3xl font-bold text-editorial-ink">{version.title}</h1>
        </div>
        <p className="text-sm text-editorial-dim">
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

      <div className="mt-10 flex items-center gap-4">
        <Link
          to={`/articles/${slug}/versions`}
          className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
        >
          &larr; Retour à l'historique
        </Link>
        <Link
          to={`/articles/${slug}`}
          className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
        >
          Voir l'article actuel
        </Link>
        <Button
          variant="outline"
          color="gray"
          size="xs"
          onClick={() => setRestoreModalOpen(true)}
        >
          Restaurer cette version
        </Button>
      </div>

      <Modal
        opened={restoreModalOpen}
        onClose={() => setRestoreModalOpen(false)}
        title="Restaurer cette version"
        centered
      >
        <p className="text-editorial-text mb-4">
          Cette action va remplacer votre brouillon actuel par le contenu de la
          version {versionNumber}. Voulez-vous continuer ?
        </p>
        <div className="flex justify-end gap-3">
          <Button
            variant="default"
            onClick={() => setRestoreModalOpen(false)}
          >
            Annuler
          </Button>
          <Button
            variant="filled"
            color="gray"
            loading={restoring}
            onClick={handleRestore}
          >
            Confirmer
          </Button>
        </div>
      </Modal>
    </div>
  );
}
