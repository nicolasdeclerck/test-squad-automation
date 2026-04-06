import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import Pagination from "../ui/Pagination";

export default function DevTracking() {
  const [issues, setIssues] = useState([]);
  const [apiError, setApiError] = useState(false);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1", 10);

  useEffect(() => {
    setLoading(true);
    api.get(`/api/core/dev-tracking/?page=${page}`).then((res) => {
      if (res.ok) {
        setIssues(res.data.results);
        setTotalPages(res.data.total_pages);
        setApiError(res.data.api_error);
      }
      setLoading(false);
    });
  }, [page]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>Suivi des devs &mdash; NICKORP</title>
        <meta name="description" content="Suivez l'avancement des d\u00e9veloppements en cours." />
      </Helmet>
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Suivi des devs</h1>

      {apiError && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-6">
          <p className="text-yellow-800 text-sm">
            Impossible de r&eacute;cup&eacute;rer les issues GitHub pour le
            moment. Veuillez r&eacute;essayer plus tard.
          </p>
        </div>
      )}

      {issues.length > 0 ? (
        <>
          <ul className="space-y-4">
            {issues.map((issue, index) => (
              <li
                key={index}
                className="border border-gray-200 rounded p-4"
              >
                <h2 className="text-lg font-semibold text-gray-900">
                  {issue.title}
                </h2>
                {issue.labels && issue.labels.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {issue.labels.map((label, li) => (
                      <span
                        key={li}
                        className="inline-block px-2 py-1 text-xs font-medium rounded"
                        style={{
                          backgroundColor: `#${label.color}`,
                          color: label.text_color,
                        }}
                      >
                        {label.name}
                      </span>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>

          <Pagination page={page} totalPages={totalPages} />
        </>
      ) : (
        !apiError && (
          <p className="text-gray-500">Aucune issue ouverte.</p>
        )
      )}
    </div>
  );
}
