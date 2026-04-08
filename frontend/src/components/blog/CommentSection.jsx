import { Avatar, Group, Text, ActionIcon } from "@mantine/core";
import { useEffect, useState } from "react";
import { api } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

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
    <div>
      <Text size="sm" c="dimmed" mb="md">
        {comments.length} commentaire{comments.length !== 1 ? "s" : ""}
      </Text>

      {comments.length > 0 ? (
        <>
          <div className="space-y-4">
            {visibleComments.map((comment) => {
              const authorName =
                comment.author.first_name && comment.author.last_name
                  ? `${comment.author.first_name} ${comment.author.last_name}`
                  : comment.author.username;

              const initial = (
                comment.author.first_name?.[0] ||
                comment.author.email?.[0] ||
                comment.author.username?.[0] ||
                "?"
              ).toUpperCase();

              return (
                <div key={comment.id}>
                  <Group>
                    <Avatar
                      src={comment.author.avatar}
                      alt={authorName}
                      radius="xl"
                      color="gray"
                    >
                      {initial}
                    </Avatar>
                    <div style={{ flex: 1 }}>
                      <Group justify="space-between" wrap="nowrap">
                        <div>
                          <Text size="sm" fw={500}>
                            {authorName}
                          </Text>
                          <Text size="xs" c="dimmed">
                            {new Date(comment.created_at).toLocaleString(
                              "fr-FR"
                            )}
                          </Text>
                        </div>
                        {comment.is_owner && (
                          <ActionIcon
                            variant="subtle"
                            color="gray"
                            size="sm"
                            onClick={() => handleDelete(comment.id)}
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
                          </ActionIcon>
                        )}
                      </Group>
                    </div>
                  </Group>
                  <Text pl={54} pt="sm" size="sm">
                    {comment.content}
                  </Text>
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
        <Text size="sm" c="dimmed">
          Aucun commentaire pour le moment.
        </Text>
      )}
    </div>
  );
}
