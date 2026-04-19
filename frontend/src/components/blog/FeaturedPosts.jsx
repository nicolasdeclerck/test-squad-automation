import { Link } from "react-router-dom";

function FeaturedAvatar({ user, size = 22 }) {
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

function FeaturedCard({ post }) {
  const authorName =
    post.author.first_name && post.author.last_name
      ? `${post.author.first_name} ${post.author.last_name}`
      : post.author.username;
  const date = new Date(
    post.published_at || post.created_at
  ).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
  const excerpt = post.plain_content
    ? post.plain_content.split(" ").slice(0, 24).join(" ") +
      (post.plain_content.split(" ").length > 24 ? "…" : "")
    : "";
  const primaryTopic =
    post.tags && post.tags.length > 0 ? post.tags[0].name.toUpperCase() : null;

  return (
    <article className="flex flex-col bg-editorial-card border border-editorial-rule h-full">
      <Link to={`/articles/${post.slug}`} className="block">
        {post.cover_image ? (
          <img
            src={post.cover_image}
            alt={post.title}
            className="w-full h-44 object-cover"
          />
        ) : (
          <div className="w-full h-44 bg-editorial-paper flex items-center justify-center">
            <span
              className="font-serif italic text-editorial-dim2"
              style={{ fontSize: 22 }}
            >
              N
            </span>
          </div>
        )}
      </Link>
      <div className="flex flex-1 flex-col p-5">
        {primaryTopic && (
          <p
            className="font-sans text-editorial-accent font-semibold mb-2"
            style={{
              fontSize: 10,
              letterSpacing: 1.6,
              textTransform: "uppercase",
            }}
          >
            {primaryTopic}
          </p>
        )}
        <h3 className="font-serif text-editorial-ink leading-tight tracking-tight text-lg">
          <Link
            to={`/articles/${post.slug}`}
            className="hover:text-editorial-ink2"
          >
            {post.title}
          </Link>
        </h3>
        {excerpt && (
          <p className="font-serif text-sm text-editorial-text mt-2 leading-relaxed flex-1">
            {excerpt}
          </p>
        )}
        <div className="flex items-center gap-2 mt-4">
          <FeaturedAvatar user={post.author} size={22} />
          <p className="font-sans text-[11px] text-editorial-dim">
            {authorName} <span className="text-editorial-dim2">·</span> {date}
          </p>
        </div>
      </div>
    </article>
  );
}

export default function FeaturedPosts({ posts }) {
  if (!posts || posts.length === 0) return null;
  return (
    <section className="mb-12">
      <div className="flex items-baseline gap-3 mb-5">
        <h2
          className="font-sans text-editorial-accent font-semibold"
          style={{
            fontSize: 11,
            letterSpacing: 2,
            textTransform: "uppercase",
          }}
        >
          À la une
        </h2>
        <span className="flex-1 h-px bg-editorial-rule" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {posts.map((post) => (
          <FeaturedCard key={post.id} post={post} />
        ))}
      </div>
    </section>
  );
}
