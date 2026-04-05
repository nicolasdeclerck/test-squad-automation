import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

export default function CommentForm({ slug, onCommentAdded }) {
  const { user } = useAuth();
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  if (!user) {
    return (
      <div className="mt-4 pt-4 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600">
          <Link
            to="/comptes/connexion"
            className="text-gray-900 font-medium hover:underline"
          >
            Connectez-vous
          </Link>{" "}
          pour poster un commentaire.
        </p>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setSubmitting(true);
    setError("");
    setSuccessMsg("");

    const res = await api.post(`/api/blog/posts/${slug}/comments/`, {
      content,
    });

    if (res.ok) {
      setContent("");
      setSuccessMsg(
        "Votre commentaire a \u00e9t\u00e9 soumis et est en attente de mod\u00e9ration."
      );
      if (onCommentAdded) onCommentAdded();
    } else {
      setError("Le commentaire n'a pas pu \u00eatre soumis.");
    }
    setSubmitting(false);
  };

  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      {successMsg && (
        <div className="mb-3 p-4 rounded-md bg-green-50 text-green-800">
          {successMsg}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            placeholder="\u00c9crivez votre commentaire..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-gray-900"
          />
          {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="px-4 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 transition-colors text-sm disabled:opacity-50"
        >
          Publier le commentaire
        </button>
      </form>
    </div>
  );
}
