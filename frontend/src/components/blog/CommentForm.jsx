import { Alert } from "@mantine/core";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

export default function CommentForm({ slug, onCommentAdded, commentsCount = 0 }) {
  const { user } = useAuth();
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [focused, setFocused] = useState(false);

  const header = (
    <div
      className="text-editorial-dim"
      style={{
        fontSize: 11,
        textTransform: "uppercase",
        letterSpacing: 1.5,
        fontWeight: 500,
        marginBottom: 18,
      }}
    >
      Commentaires · {commentsCount}
    </div>
  );

  if (!user) {
    return (
      <div>
        {header}
        <div
          className="text-editorial-text"
          style={{
            border: "1px solid rgb(var(--color-editorial-rule))",
            padding: 14,
            background: "rgb(var(--color-editorial-card))",
            fontSize: 13,
            lineHeight: 1.55,
          }}
        >
          <Link
            to="/comptes/connexion"
            className="text-editorial-ink font-medium hover:underline"
          >
            Connectez-vous
          </Link>{" "}
          pour laisser un commentaire.
        </div>
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
      setFocused(false);
      setSuccessMsg(
        "Votre commentaire a été soumis et est en attente de modération."
      );
      if (onCommentAdded) onCommentAdded();
    } else {
      setError("Le commentaire n'a pas pu être soumis.");
    }
    setSubmitting(false);
  };

  const expanded = focused || content.length > 0;

  return (
    <div>
      {header}
      {successMsg && (
        <Alert color="green" mb="sm" variant="light" radius={2}>
          {successMsg}
        </Alert>
      )}
      <form
        onSubmit={handleSubmit}
        style={{
          border: "1px solid rgb(var(--color-editorial-rule))",
          background: "rgb(var(--color-editorial-card))",
          padding: 14,
        }}
      >
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => !content && setFocused(false)}
          placeholder="Laisser un commentaire…"
          rows={expanded ? 3 : 1}
          style={{
            width: "100%",
            border: "none",
            outline: "none",
            resize: "vertical",
            fontFamily: '"Inter", system-ui, sans-serif',
            fontSize: 13,
            lineHeight: 1.55,
            color: "rgb(var(--color-editorial-text))",
            background: "transparent",
            fontStyle: content ? "normal" : "italic",
          }}
        />
        {error && (
          <div className="text-red-600 dark:text-red-400 text-xs mt-1">{error}</div>
        )}
        {expanded && (
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginTop: 10,
            }}
          >
            <button
              type="submit"
              disabled={submitting || !content.trim()}
              style={{
                fontFamily: '"Inter", system-ui, sans-serif',
                fontSize: 12,
                fontWeight: 500,
                background: "rgb(var(--color-editorial-ink))",
                color: "rgb(var(--color-editorial-paper))",
                border: "none",
                padding: "6px 12px",
                borderRadius: 3,
                cursor: "pointer",
                opacity: submitting || !content.trim() ? 0.5 : 1,
                transition: "opacity 120ms ease",
              }}
            >
              {submitting ? "Publication…" : "Publier"}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
