import { Alert, Button, Textarea } from "@mantine/core";
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
      <div className="text-center py-4">
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
        "Votre commentaire a été soumis et est en attente de modération."
      );
      if (onCommentAdded) onCommentAdded();
    } else {
      setError("Le commentaire n'a pas pu être soumis.");
    }
    setSubmitting(false);
  };

  return (
    <div>
      {successMsg && (
        <Alert color="green" mb="sm">
          {successMsg}
        </Alert>
      )}
      <form onSubmit={handleSubmit}>
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={3}
          placeholder="Écrivez votre commentaire..."
          error={error || undefined}
          mb="sm"
        />
        <Button
          type="submit"
          loading={submitting}
          color="dark"
          size="sm"
        >
          Publier le commentaire
        </Button>
      </form>
    </div>
  );
}
