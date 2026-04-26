import { Link } from "react-router-dom";

function OwnerIcon({ d, filled = false }) {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={d} />
    </svg>
  );
}

export default function OwnerActions({
  post,
  user,
  publishing,
  onPublish,
  pinToggling,
  onTogglePin,
  hasVersions,
  hasDraftChanges,
}) {
  if (!post?.is_owner || !user?.is_superuser) return null;

  const base = {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    fontFamily: '"Inter", system-ui, sans-serif',
    fontSize: 12,
    fontWeight: 500,
    padding: "6px 10px",
    borderRadius: 3,
    cursor: "pointer",
    whiteSpace: "nowrap",
    textDecoration: "none",
  };
  const neutral = {
    ...base,
    border: "1px solid rgb(var(--color-editorial-rule))",
    background: "rgb(var(--color-editorial-card))",
    color: "rgb(var(--color-editorial-text))",
  };
  const primary = {
    ...base,
    border: "1px solid rgb(var(--color-editorial-ink))",
    background: "rgb(var(--color-editorial-ink))",
    color: "rgb(var(--color-editorial-paper))",
  };
  const canPublishDraft = post.status === "draft";
  const canPublishChanges = post.status === "published" && post.has_draft;

  return (
    <div
      data-testid="owner-actions"
      className="md:sticky md:top-[var(--header-height)] md:z-[var(--z-owner-actions)]"
      style={{
        display: "flex",
        gap: 6,
        flexWrap: "wrap",
        alignItems: "center",
        padding: "10px 0",
        borderTop: "1px solid rgb(var(--color-editorial-rule))",
        borderBottom: "1px solid rgb(var(--color-editorial-rule))",
        margin: "28px 0",
        background: "rgb(var(--color-editorial-paper))",
      }}
    >
      <span
        style={{
          fontFamily: '"Inter", system-ui, sans-serif',
          fontSize: 11,
          color: "rgb(var(--color-editorial-dim))",
          textTransform: "uppercase",
          letterSpacing: 1,
          fontWeight: 500,
          alignSelf: "center",
          marginRight: 8,
        }}
      >
        Auteur
      </span>

      <Link to={`/articles/${post.slug}/modifier`} style={neutral} title="Modifier">
        <OwnerIcon d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Z" />
        <span>Modifier</span>
      </Link>

      {(canPublishDraft || canPublishChanges) && (
        <button
          type="button"
          onClick={onPublish}
          disabled={publishing}
          style={{ ...primary, opacity: publishing ? 0.6 : 1 }}
          title={canPublishChanges ? "Publier les modifications" : "Publier"}
        >
          <OwnerIcon d="M12 19.5v-15m0 0-6.75 6.75M12 4.5l6.75 6.75" />
          <span>
            {publishing
              ? "Publication…"
              : canPublishChanges
                ? "Publier les modifications"
                : "Publier"}
          </span>
        </button>
      )}

      {post.status === "published" && (
        <button
          type="button"
          onClick={onTogglePin}
          disabled={pinToggling}
          style={{ ...neutral, opacity: pinToggling ? 0.6 : 1 }}
          title={post.is_pinned ? "Désépingler" : "Épingler à la une"}
        >
          <OwnerIcon
            d="M9 4.5v4.5l-3 3v2.25h12V12l-3-3V4.5m-6 9v6"
            filled={post.is_pinned}
          />
          <span>{post.is_pinned ? "Désépingler" : "Épingler"}</span>
        </button>
      )}

      {hasVersions && (
        <Link to={`/articles/${post.slug}/versions`} style={neutral} title="Versions">
          <OwnerIcon d="M12 6v6h4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          <span>Versions</span>
        </Link>
      )}

      <Link
        to={`/articles/${post.slug}/supprimer`}
        style={neutral}
        title="Supprimer"
      >
        <OwnerIcon d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0c.342.052.682.107 1.022.166m-16.5-.165c.34-.059.68-.114 1.022-.165m14.456 0a48.108 48.108 0 0 0-3.478-.397M5.794 5.625a48.11 48.11 0 0 1 3.478-.397M15.272 5.228v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916" />
        <span>Supprimer</span>
      </Link>

      <div style={{ flex: 1 }} />

      {hasDraftChanges && (
        <span
          style={{
            fontFamily: '"Inter", system-ui, sans-serif',
            fontSize: 11,
            color: "rgb(var(--color-editorial-accent))",
            alignSelf: "center",
            fontStyle: "italic",
          }}
        >
          Modifications non publiées
        </span>
      )}
    </div>
  );
}
