import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";

export default function PostCard({ post }) {
  const { user } = useAuth();
  const isOwner = user && post.author && user.id === post.author.id;

  const authorName =
    post.author.first_name && post.author.last_name
      ? `${post.author.first_name} ${post.author.last_name}`
      : post.author.email || post.author.username;

  const date = new Date(post.created_at).toLocaleDateString("fr-FR");

  return (
    <article className="card">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            <Link
              to={`/articles/${post.slug}`}
              className="hover:underline"
            >
              {post.title}
            </Link>
          </h2>
          <div className="flex items-center gap-2 mt-1">
            <Avatar user={post.author} size="sm" />
            <p className="text-sm text-gray-500">
              {authorName} &mdash; {date}
            </p>
          </div>
        </div>
        {isOwner && (
          <div className="flex items-center gap-2 ml-4 shrink-0">
            <Link
              to={`/articles/${post.slug}/modifier`}
              className="text-gray-400 hover:text-black transition-colors"
              title="Modifier"
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
                  d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
                />
              </svg>
            </Link>
            <Link
              to={`/articles/${post.slug}/supprimer`}
              className="text-gray-400 hover:text-black transition-colors"
              title="Supprimer"
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
                  d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                />
              </svg>
            </Link>
          </div>
        )}
      </div>
      <p className="text-gray-600 mt-3 leading-relaxed">
        {post.plain_content
          ? post.plain_content.split(" ").slice(0, 50).join(" ") +
            (post.plain_content.split(" ").length > 50 ? "..." : "")
          : ""}
      </p>
    </article>
  );
}
