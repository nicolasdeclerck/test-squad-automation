import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { useCreateBlockNote } from "@blocknote/react";
import { Alert } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import DOMPurify from "dompurify";
import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";
import { buildHeadingIndex } from "../../utils/articleToc";
import ArticleToc from "./ArticleToc";
import CommentForm from "./CommentForm";
import CommentSection from "./CommentSection";

function BlockNoteRenderer({ content, onHeadings }) {
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
    if (!validBlocks && onHeadings) {
      onHeadings([]);
    }
  }, [validBlocks, onHeadings]);

  useEffect(() => {
    if (editor && validBlocks) {
      editor
        .blocksToFullHTML(editor.document)
        .then((rawHtml) => {
          const sanitized = DOMPurify.sanitize(rawHtml);
          const { items, html: enrichedHtml } = buildHeadingIndex(sanitized);
          setHtml(enrichedHtml);
          if (onHeadings) onHeadings(items);
        })
        .catch(() => {});
    }
  }, [editor, validBlocks, onHeadings]);

  if (!validBlocks) {
    return (
      <div className="article-prose whitespace-pre-line">{content}</div>
    );
  }

  return (
    <div
      className="article-prose"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

function AuthorAvatar({ user, size = 36 }) {
  const initial = (
    user.first_name?.[0] ||
    user.email?.[0] ||
    user.username?.[0] ||
    "?"
  ).toUpperCase();

  if (user.avatar) {
    return (
      <img
        src={user.avatar}
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
        background: "rgb(var(--color-editorial-avatar-bg))",
        color: "rgb(var(--color-editorial-avatar-fg))",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: Math.round(size * 0.36),
        fontWeight: 600,
        flexShrink: 0,
      }}
    >
      {initial}
    </div>
  );
}

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

function OwnerActions({
  post,
  publishing,
  onPublish,
  pinToggling,
  onTogglePin,
  hasVersions,
  hasDraftChanges,
}) {
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
    transition: "background-color 120ms ease, border-color 120ms ease",
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
      style={{
        display: "flex",
        gap: 6,
        flexWrap: "wrap",
        alignItems: "center",
        padding: "10px 0",
        borderTop: "1px solid rgb(var(--color-editorial-rule))",
        borderBottom: "1px solid rgb(var(--color-editorial-rule))",
        margin: "28px 0",
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

export default function PostDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [publishing, setPublishing] = useState(false);
  const [publishError, setPublishError] = useState("");
  const [hasVersions, setHasVersions] = useState(false);
  const [pinToggling, setPinToggling] = useState(false);
  const [headings, setHeadings] = useState([]);

  const handlePublish = async () => {
    setPublishing(true);
    setPublishError("");
    const res = await api.post(`/api/blog/posts/${post.slug}/publish/`);
    if (res.ok) {
      setPost(res.data);
    } else {
      setPublishError(res.errors?.error || "Erreur lors de la publication.");
    }
    setPublishing(false);
  };

  const handleTogglePin = async () => {
    if (!post || pinToggling) return;
    setPinToggling(true);
    const res = post.is_pinned
      ? await api.delete(`/api/blog/posts/${post.slug}/pin/`)
      : await api.post(`/api/blog/posts/${post.slug}/pin/`);
    setPinToggling(false);
    if (res.ok) {
      setPost(res.data);
    } else {
      notifications.show({
        title: "Épinglage impossible",
        message:
          res.errors?.error ||
          res.errors?.detail ||
          "Erreur lors de l'épinglage.",
        color: "red",
      });
    }
  };

  useEffect(() => {
    if (!post) setLoading(true);
    api.get(`/api/blog/posts/${slug}/`).then((res) => {
      if (res.ok) {
        setPost(res.data);
      }
      setLoading(false);
    });
  }, [slug, refreshKey]);

  useEffect(() => {
    if (post?.is_owner) {
      api.get(`/api/blog/posts/${slug}/versions/`).then((res) => {
        if (res.ok && res.data.count > 0) {
          setHasVersions(true);
        }
      });
    }
  }, [post?.is_owner, slug]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-editorial-dim text-center">Chargement…</p>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-editorial-dim text-center">Article introuvable.</p>
      </div>
    );
  }

  const authorName =
    post.author.first_name && post.author.last_name
      ? `${post.author.first_name} ${post.author.last_name}`
      : post.author.username;

  const displayTitle =
    post.is_owner && post.status === "draft" && !post.title && post.draft_title
      ? post.draft_title
      : post.title;
  const displayContent =
    post.is_owner &&
    post.status === "draft" &&
    !post.content &&
    post.draft_content
      ? post.draft_content
      : post.content;

  const primaryTopic =
    post.tags && post.tags.length > 0 ? post.tags[0].name : null;
  const otherTopics =
    post.tags && post.tags.length > 1
      ? post.tags.slice(1).map((t) => t.name).join(" · ")
      : null;
  const topicLine = [primaryTopic, otherTopics].filter(Boolean).join(" · ");

  const publishedDate = post.published_at || post.created_at;
  const readingMinutes = post.reading_time_minutes;
  const isOwnerSuperuser = post.is_owner && user?.is_superuser;
  const hasDraftChanges = post.status === "published" && post.has_draft;

  return (
    <div className="bg-editorial-paper">
      <Helmet>
        <title>{displayTitle}</title>
        <meta
          name="description"
          content={
            primaryTopic
              ? `${primaryTopic.toUpperCase()} — ${displayTitle}`
              : displayTitle
          }
        />
      </Helmet>

      <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-12 lg:py-16">
        <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_320px] lg:gap-16">
          <article className="min-w-0">
            {topicLine && (
              <p
                className="font-sans text-editorial-accent font-semibold mb-3"
                style={{
                  fontSize: 11,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                }}
              >
                {topicLine}
              </p>
            )}

            <h1
              className="font-serif text-editorial-ink"
              style={{
                fontSize: "clamp(32px, 4.6vw, 54px)",
                lineHeight: 1.05,
                fontWeight: 600,
                letterSpacing: "-0.02em",
                margin: "0 0 20px",
                maxWidth: 720,
              }}
            >
              {displayTitle}
            </h1>

            <div
              className="flex items-center gap-3"
              style={{
                fontFamily: '"Inter", system-ui, sans-serif',
                paddingBottom: 16,
              }}
            >
              <AuthorAvatar user={post.author} size={36} />
              <div>
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 500,
                    color: "rgb(var(--color-editorial-ink2))",
                  }}
                >
                  {authorName}
                </div>
                <div style={{ fontSize: 12, color: "rgb(var(--color-editorial-dim))" }}>
                  {new Date(publishedDate).toLocaleDateString("fr-FR", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                  {readingMinutes ? ` · ${readingMinutes} min de lecture` : ""}
                </div>
              </div>
            </div>

            {isOwnerSuperuser && (
              <OwnerActions
                post={post}
                publishing={publishing}
                onPublish={handlePublish}
                pinToggling={pinToggling}
                onTogglePin={handleTogglePin}
                hasVersions={hasVersions}
                hasDraftChanges={hasDraftChanges}
              />
            )}

            {isOwnerSuperuser && hasDraftChanges && (
              <Alert color="blue" className="mb-6">
                Cet article a des modifications non publiées.{" "}
                <Link
                  to={`/articles/${post.slug}/modifier`}
                  className="underline font-medium"
                >
                  Voir les modifications
                </Link>
              </Alert>
            )}

            {publishError && (
              <p className="text-red-600 text-sm mb-4">{publishError}</p>
            )}

            {post.cover_image && (
              <img
                src={post.cover_image}
                alt={displayTitle}
                className="w-full h-auto object-cover mb-10"
                style={{ maxHeight: 480 }}
              />
            )}

            <BlockNoteRenderer
              content={displayContent}
              onHeadings={setHeadings}
            />

            <div
              className="mt-14 pt-6"
              style={{
                borderTop: "1px solid rgb(var(--color-editorial-rule))",
                fontFamily: '"Inter", system-ui, sans-serif',
              }}
            >
              <Link
                to="/"
                className="text-editorial-dim hover:text-editorial-ink transition-colors"
                style={{ fontSize: 13 }}
              >
                ← Retour aux articles
              </Link>
            </div>
          </article>

          {post.status !== "draft" && (
            <aside
              className="mt-16 lg:mt-0"
              style={{
                fontFamily: '"Inter", system-ui, sans-serif',
                paddingTop: 0,
              }}
            >
              <div className="lg:sticky lg:top-24 border-t border-editorial-rule lg:border-t-0 pt-12 lg:pt-0">
                <ArticleToc items={headings} />
                <CommentForm
                  slug={post.slug}
                  onCommentAdded={() => setRefreshKey((k) => k + 1)}
                  commentsCount={post.approved_comments?.length || 0}
                />
                <div className="mt-7">
                  <CommentSection
                    comments={post.approved_comments}
                    slug={post.slug}
                  />
                </div>
              </div>
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}
