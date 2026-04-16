import { Badge } from "@mantine/core";
import { Link } from "react-router-dom";
import Avatar from "../ui/Avatar";

function FeaturedCard({ post }) {
  const authorName =
    post.author.first_name && post.author.last_name
      ? `${post.author.first_name} ${post.author.last_name}`
      : post.author.username;
  const date = new Date(
    post.published_at || post.created_at
  ).toLocaleDateString("fr-FR");
  const excerpt = post.plain_content
    ? post.plain_content.split(" ").slice(0, 30).join(" ") +
      (post.plain_content.split(" ").length > 30 ? "..." : "")
    : "";

  return (
    <article className="flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm hover:shadow-md transition-shadow">
      <Link to={`/articles/${post.slug}`} className="block">
        {post.cover_image ? (
          <img
            src={post.cover_image}
            alt={post.title}
            className="w-full h-56 object-cover"
          />
        ) : (
          <div className="w-full h-56 bg-gradient-to-br from-blue-50 to-gray-100" />
        )}
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <h3 className="text-lg font-semibold text-gray-900">
          <Link
            to={`/articles/${post.slug}`}
            className="hover:underline"
          >
            {post.title}
          </Link>
        </h3>
        {post.tags && post.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {post.tags.map((tag) => (
              <Badge key={tag.id} size="xs" variant="light" color="blue">
                {tag.name}
              </Badge>
            ))}
          </div>
        )}
        {excerpt && (
          <p className="text-sm text-gray-600 mt-3 leading-relaxed flex-1">
            {excerpt}
          </p>
        )}
        <div className="flex items-center gap-2 mt-4">
          <Avatar user={post.author} size="sm" />
          <p className="text-xs text-gray-500">
            {authorName} &mdash; {date}
          </p>
        </div>
      </div>
    </article>
  );
}

export default function FeaturedPosts({ posts }) {
  if (!posts || posts.length === 0) return null;
  return (
    <section className="mb-10">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        À la une
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post) => (
          <FeaturedCard key={post.id} post={post} />
        ))}
      </div>
    </section>
  );
}
