import { useEffect, useState } from "react";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";
import Avatar from "../ui/Avatar";

export default function CommentSection({ comments: initialComments, slug }) {
  const { user } = useAuth();
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

  return (
    <div className="mt-10 border-t border-gray-200 pt-4">
      <h2 className="text-sm text-gray-500 mb-4">
        {comments.length} commentaire{comments.length !== 1 ? "s" : ""}
      </h2>

      {comments.length > 0 ? (
        <>
          <div className="divide-y divide-gray-100">
            {visibleComments.map((comment, index) => {
              const authorName =
                comment.author.first_name && comment.author.last_name
                  ? `${comment.author.first_name} ${comment.author.last_name}`
                  : comment.author.username;

              return (
                <div
                  key={comment.id}
                  className={`py-3 ${index === 0 ? "pt-0" : ""}`}
                >
                  <div className="flex items-start gap-3">
                    <Avatar user={comment.author} size="md" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-gray-900">
                          {authorName}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(comment.created_at).toLocaleString("fr-FR")}
                        </span>
                        {comment.is_owner && (
                          <button
                            onClick={() => handleDelete(comment.id)}
                            className="ml-auto text-gray-400 hover:text-red-500 transition-colors"
                            title="Supprimer"
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
                      <p className="text-sm text-gray-700">{comment.content}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {visibleCount < comments.length && (
            <div className="mt-4 text-center">
              <button
                onClick={() => setVisibleCount((prev) => prev + 10)}
                className="text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                Voir les 10 commentaires suivants
              </button>
            </div>
          )}
        </>
      ) : (
        <p className="text-sm text-gray-500">
          Aucun commentaire pour le moment.
        </p>
      )}
    </div>
  );
}
