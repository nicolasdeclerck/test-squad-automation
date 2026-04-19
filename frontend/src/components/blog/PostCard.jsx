import { Menu } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

function CardAvatar({ user, size = 24 }) {
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
        fontSize: Math.round(size * 0.42),
        fontWeight: 600,
        flexShrink: 0,
      }}
    >
      {initial}
    </div>
  );
}

export default function PostCard({ post: initialPost, onChange }) {
  const { user } = useAuth();
  const [post, setPost] = useState(initialPost);
  const [pinToggling, setPinToggling] = useState(false);
  const canEdit =
    user && user.is_superuser && post.author && user.id === post.author.id;
  const canPin = canEdit && post.status === "published";

  const handleTogglePin = async () => {
    if (pinToggling) return;
    setPinToggling(true);
    const res = post.is_pinned
      ? await api.delete(`/api/blog/posts/${post.slug}/pin/`)
      : await api.post(`/api/blog/posts/${post.slug}/pin/`);
    setPinToggling(false);
    if (res.ok) {
      setPost(res.data);
      if (onChange) onChange(res.data);
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

  const authorName =
    post.author.first_name && post.author.last_name
      ? `${post.author.first_name} ${post.author.last_name}`
      : post.author.username;

  const date = new Date(
    post.published_at || post.created_at
  ).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const primaryTopic =
    post.tags && post.tags.length > 0
      ? post.tags
          .slice(0, 3)
          .map((t) => t.name)
          .join(" · ")
          .toUpperCase()
      : null;

  const excerpt = post.plain_content
    ? post.plain_content.split(" ").slice(0, 38).join(" ") +
      (post.plain_content.split(" ").length > 38 ? "…" : "")
    : "";

  return (
    <article className="card flex gap-6">
      <div className="flex-1 min-w-0">
        {primaryTopic && (
          <p
            className="font-sans text-editorial-accent font-semibold mb-2"
            style={{
              fontSize: 11,
              letterSpacing: 1.6,
              textTransform: "uppercase",
            }}
          >
            {primaryTopic}
          </p>
        )}

        <div className="flex items-start justify-between gap-3">
          <h2 className="font-serif text-editorial-ink text-2xl leading-tight tracking-tight">
            <Link
              to={`/articles/${post.slug}`}
              className="hover:text-editorial-ink2"
            >
              {post.title}
            </Link>
          </h2>
          {canEdit && (
            <Menu position="bottom-end" shadow="md" width={200}>
              <Menu.Target>
                <button
                  className="text-editorial-dim2 hover:text-editorial-ink transition-colors shrink-0 mt-1"
                  title="Actions"
                  aria-label="Actions"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="size-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z"
                    />
                  </svg>
                </button>
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Item
                  component={Link}
                  to={`/articles/${post.slug}/modifier`}
                  leftSection={
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="size-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
                      />
                    </svg>
                  }
                >
                  Modifier
                </Menu.Item>
                {canPin && (
                  <Menu.Item
                    onClick={handleTogglePin}
                    disabled={pinToggling}
                    leftSection={
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill={post.is_pinned ? "currentColor" : "none"}
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-5"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M9 4.5v4.5l-3 3v2.25h12V12l-3-3V4.5m-6 9v6m3-10.5h.008v.008H12V7.5Z"
                        />
                      </svg>
                    }
                  >
                    {post.is_pinned ? "Désépingler" : "Épingler à la une"}
                  </Menu.Item>
                )}
                <Menu.Item
                  component={Link}
                  to={`/articles/${post.slug}/supprimer`}
                  color="red"
                  leftSection={
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="size-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                      />
                    </svg>
                  }
                >
                  Supprimer
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          )}
        </div>

        {excerpt && (
          <p className="font-serif text-editorial-text mt-3 leading-relaxed text-[17px]">
            {excerpt}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-x-3 gap-y-2 mt-4">
          <div className="flex items-center gap-2">
            <CardAvatar user={post.author} size={24} />
            <p className="font-sans text-xs text-editorial-dim">
              {authorName}{" "}
              <span className="text-editorial-dim2">·</span> {date}
            </p>
          </div>
          {post.is_pinned && (
            <span
              className="inline-flex items-center gap-1 text-[10px] tracking-[1.4px] uppercase font-semibold text-editorial-accent"
              title="Article épinglé à la une"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="size-3"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 4.5v4.5l-3 3v2.25h12V12l-3-3V4.5m-6 9v6m3-10.5h.008v.008H12V7.5Z"
                />
              </svg>
              Épinglé
            </span>
          )}
          {canEdit && post.has_draft && post.status === "published" && (
            <span
              className="inline-flex items-center gap-1 text-[10px] tracking-[1.4px] uppercase font-semibold text-editorial-accent italic"
              title="Brouillon en cours"
            >
              Brouillon en cours
            </span>
          )}
        </div>
      </div>

      {post.cover_image && (
        <Link
          to={`/articles/${post.slug}`}
          className="hidden sm:block shrink-0 w-40 h-28 overflow-hidden"
        >
          <img
            src={post.cover_image}
            alt={post.title}
            className="w-full h-full object-cover"
          />
        </Link>
      )}
    </article>
  );
}
