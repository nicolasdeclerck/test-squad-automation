import { Button, Modal } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";
import BlockNoteRenderer from "./BlockNoteRenderer";

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

      <BlockNoteRenderer key={version.content} content={version.content} />

      <div className="mt-10 flex items-center gap-4">
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
        <Button
          variant="outline"
          color="dark"
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
        <p className="text-gray-700 mb-4">
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
            color="dark"
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
