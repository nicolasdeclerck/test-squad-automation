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
import OwnerActions from "./OwnerActions";

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

function LinkedInShareButton({ title }) {
  const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
    window.location.origin + window.location.pathname,
  )}`;

  return (
    <div
      style={{
        marginTop: 56,
        display: "flex",
        alignItems: "center",
        gap: 12,
        flexWrap: "wrap",
        fontFamily: '"Inter", system-ui, sans-serif',
      }}
    >
      <span
        style={{
          fontSize: 11,
          color: "rgb(var(--color-editorial-dim))",
          textTransform: "uppercase",
          letterSpacing: 1,
          fontWeight: 500,
        }}
      >
        Partager
      </span>
      <a
        href={shareUrl}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Partager « ${title} » sur LinkedIn`}
        title="Partager sur LinkedIn"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          fontSize: 12,
          fontWeight: 500,
          padding: "6px 10px",
          borderRadius: 3,
          textDecoration: "none",
          border: "1px solid rgb(var(--color-editorial-rule))",
          background: "rgb(var(--color-editorial-card))",
          color: "rgb(var(--color-editorial-text))",
          transition: "background-color 120ms ease, border-color 120ms ease",
        }}
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.852 3.37-1.852 3.601 0 4.267 2.37 4.267 5.455v6.288zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.063 2.063 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
        </svg>
        <span>LinkedIn</span>
      </a>
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

            <OwnerActions
              post={post}
              user={user}
              publishing={publishing}
              onPublish={handlePublish}
              pinToggling={pinToggling}
              onTogglePin={handleTogglePin}
              hasVersions={hasVersions}
              hasDraftChanges={hasDraftChanges}
            />

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

            <div className="lg:hidden pb-4">
              <ArticleToc items={headings} collapsible />
            </div>

            <BlockNoteRenderer
              content={displayContent}
              onHeadings={setHeadings}
            />

            {post.status === "published" && (
              <LinkedInShareButton title={displayTitle} />
            )}

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
              <div className="hidden lg:block lg:sticky lg:top-[var(--header-height)]">
                <ArticleToc items={headings} />
              </div>
              <div className="border-t border-editorial-rule lg:border-t-0 pt-12 lg:pt-0">
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
