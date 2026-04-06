import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";

export default function PostDelete() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get(`/api/blog/posts/${slug}/`).then((res) => {
      if (res.ok) {
        if (!res.data.is_owner) {
          navigate("/", { replace: true });
          return;
        }
        setPost(res.data);
      }
      setLoading(false);
    });
  }, [slug, navigate]);

  const handleDelete = async () => {
    if (
      !window.confirm(
        "\u00cates-vous s\u00fbr de vouloir supprimer cet article ?"
      )
    ) {
      return;
    }
    const res = await api.delete(`/api/blog/posts/${slug}/`);
    if (res.ok) {
      navigate("/");
    } else {
      setError("Impossible de supprimer cet article.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Article introuvable.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Supprimer l&apos;article
      </h1>

      <div className="card">
        <p className="text-gray-700">
          \u00cates-vous s\u00fbr de vouloir supprimer l&apos;article{" "}
          <strong>&laquo; {post.title} &raquo;</strong> ?
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Cette action est irr\u00e9versible.
        </p>

        {error && (
          <p className="text-red-600 text-sm mt-2">{error}</p>
        )}

        <div className="mt-6 flex gap-4">
          <button
            onClick={handleDelete}
            className="btn-primary bg-black text-white px-6 py-2"
          >
            Supprimer
          </button>
          <Link
            to="/"
            className="btn-primary bg-white text-black border border-black px-6 py-2"
          >
            Annuler
          </Link>
        </div>
      </div>
    </div>
  );
}
