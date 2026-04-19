import { useEffect, useState } from "react";
import { api } from "../../api/client";

function CommentAvatar({ author, size = 28 }) {
  const initial = (
    author.first_name?.[0] ||
    author.email?.[0] ||
    author.username?.[0] ||
    "?"
  ).toUpperCase();

  if (author.avatar) {
    return (
      <img
        src={author.avatar}
        alt=""
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          objectFit: "cover",
          flexShrink: 0,
        }}
      />
    );
  }

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: "#e3eee0",
        color: "#1f1f1f",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: Math.round(size * 0.4),
        fontWeight: 600,
        flexShrink: 0,
      }}
    >
      {initial}
    </div>
  );
}

function formatRelative(dateStr) {
  const date = new Date(dateStr);
  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.round(diffMs / 60000);
  const diffH = Math.round(diffMs / 3600000);
  const diffD = Math.round(diffMs / 86400000);
  if (diffMin < 1) return "à l'instant";
  if (diffMin < 60) return `il y a ${diffMin} min`;
  if (diffH < 24) return `il y a ${diffH} heure${diffH > 1 ? "s" : ""}`;
  if (diffD === 1) return "hier";
  if (diffD < 7) return `il y a ${diffD} jours`;
  return date.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function CommentSection({ comments: initialComments, slug: _slug }) {
  const [comments, setComments] = useState(initialComments || []);
  const [visibleCount, setVisibleCount] = useState(10);

  useEffect(() => {
    setComments(initialComments || []);
  }, [initialComments]);

  const handleDelete = async (commentId) => {
    const res = await api.delete(`/api/blog/comments/${commentId}/`);
    if (res.ok) {
      setComments((prev) => prev.filter((c) => c.id !== commentId));
    }
  };

  const visibleComments = comments.slice(0, visibleCount);

  if (comments.length === 0) {
    return (
      <div
        className="text-editorial-dim"
        style={{
          fontSize: 13,
          fontStyle: "italic",
          lineHeight: 1.55,
        }}
      >
        Aucun commentaire pour le moment.
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {visibleComments.map((comment) => {
          const authorName =
            comment.author.first_name && comment.author.last_name
              ? `${comment.author.first_name} ${comment.author.last_name}`
              : comment.author.username;

          return (
            <div key={comment.id}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 6,
                }}
              >
                <CommentAvatar author={comment.author} size={28} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 13,
                      fontWeight: 500,
                      color: "#1f1f1f",
                    }}
                  >
                    {authorName}
                  </div>
                  <div style={{ fontSize: 11, color: "#6b6b6b" }}>
                    {formatRelative(comment.created_at)}
                  </div>
                </div>
                {comment.is_owner && (
                  <button
                    type="button"
                    onClick={() => handleDelete(comment.id)}
                    title="Supprimer"
                    aria-label="Supprimer le commentaire"
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#9a9a9a",
                      cursor: "pointer",
                      padding: 4,
                      display: "inline-flex",
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="w-4 h-4"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M6 18 18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                )}
              </div>
              <div
                style={{
                  fontSize: 14,
                  lineHeight: 1.55,
                  color: "#2a2a2a",
                  paddingLeft: 38,
                }}
              >
                {comment.content}
              </div>
            </div>
          );
        })}
      </div>

      {visibleCount < comments.length && (
        <div style={{ marginTop: 20, textAlign: "center" }}>
          <button
            type="button"
            onClick={() => setVisibleCount((prev) => prev + 10)}
            style={{
              fontFamily: '"Inter", system-ui, sans-serif',
              fontSize: 12,
              color: "#6b6b6b",
              background: "transparent",
              border: "none",
              cursor: "pointer",
              textDecoration: "underline",
              textUnderlineOffset: 3,
            }}
          >
            Voir les 10 commentaires suivants
          </button>
        </div>
      )}
    </div>
  );
}
