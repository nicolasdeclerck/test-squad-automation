import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api/client";

export default function VersionHistory() {
  const { slug } = useParams();
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get(`/api/blog/posts/${slug}/versions/`).then((res) => {
      if (res.ok) {
        setVersions(res.data);
      } else {
        setError("Impossible de charger l'historique des versions.");
      }
      setLoading(false);
    });
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-red-600 text-center">{error}</p>
        <div className="mt-6 text-center">
          <Link
            to={`/articles/${slug}`}
            className="text-sm text-gray-500 hover:text-black transition-colors"
          >
            &larr; Retour à l'article
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>Historique des versions</title>
      </Helmet>

      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Historique des versions
      </h1>

      {versions.length === 0 ? (
        <p className="text-gray-500">Aucune version publiée.</p>
      ) : (
        <div className="space-y-4">
          {versions.map((version) => (
            <Link
              key={version.version_number}
              to={`/articles/${slug}/versions/${version.version_number}`}
              className="block border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-black text-white text-sm font-medium shrink-0">
                  {version.version_number}
                </span>
                <div className="min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {version.title}
                  </p>
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
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-10">
        <Link
          to={`/articles/${slug}`}
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          &larr; Retour à l'article
        </Link>
      </div>
    </div>
  );
}
