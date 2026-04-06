import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";
import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";
import CommentForm from "./CommentForm";
import CommentSection from "./CommentSection";
import { schema } from "./mermaid-block";

function BlockNoteRenderer({ content }) {
  const blocks = useMemo(() => {
    try {
      return JSON.parse(content);
    } catch {
      return null;
    }
  }, [content]);

  const editor = useCreateBlockNote({
    schema,
    initialContent: blocks || undefined,
  });

  if (!blocks) {
    return <div className="whitespace-pre-line">{content}</div>;
  }

  return (
    <BlockNoteView
      editor={editor}
      editable={false}
      theme="light"
    />
  );
}

export default function PostDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    api.get(`/api/blog/posts/${slug}/`).then((res) => {
      if (res.ok) {
        setPost(res.data);
      }
      setLoading(false);
    });
  }, [slug, refreshKey]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Article introuvable.</p>
      </div>
    );
  }

  const authorName =
    post.author.first_name && post.author.last_name
      ? `${post.author.first_name} ${post.author.last_name}`
      : post.author.username;

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>{post.title}</title>
        <meta name="description" content={post.title} />
      </Helmet>

      <article>
        <div className="flex items-start justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">{post.title}</h1>
          {post.is_owner && (
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

        <div className="flex items-center gap-2 mb-8">
          <Avatar user={post.author} size="md" />
          <p className="text-sm text-gray-500">
            {authorName} &mdash;{" "}
            {new Date(post.created_at).toLocaleDateString("fr-FR")}
          </p>
        </div>

        <BlockNoteRenderer content={post.content} />
      </article>

      <CommentSection
        comments={post.approved_comments}
        slug={post.slug}
      />

      <CommentForm
        slug={post.slug}
        onCommentAdded={() => setRefreshKey((k) => k + 1)}
      />

      <div className="mt-10">
        <Link
          to="/"
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          &larr; Retour aux articles
        </Link>
      </div>
    </div>
  );
}
