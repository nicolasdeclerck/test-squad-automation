import { useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import Pagination from "../ui/Pagination";
import FeaturedPosts from "./FeaturedPosts";
import PostCard from "./PostCard";

export default function PostList({ isHome = false }) {
  const [posts, setPosts] = useState([]);
  const [pinnedPosts, setPinnedPosts] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [showFullListLink, setShowFullListLink] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1", 10);

  const fetchPinned = useCallback(() => {
    if (!isHome) return;
    api.get("/api/blog/posts/pinned/").then((res) => {
      if (res.ok) {
        setPinnedPosts(Array.isArray(res.data) ? res.data : []);
      }
    });
  }, [isHome]);

  useEffect(() => {
    setLoading(true);
    const url = isHome
      ? "/api/blog/posts/?page=1"
      : `/api/blog/posts/?page=${page}`;

    api.get(url).then((res) => {
      if (res.ok) {
        setPosts(res.data.results);
        const total = Math.ceil(res.data.count / 10);
        setTotalPages(total);
        if (isHome) {
          setShowFullListLink(res.data.count > 10);
        }
      }
      setLoading(false);
    });
    fetchPinned();
  }, [page, isHome, fetchPinned]);

  const handlePostChange = useCallback(
    (updated) => {
      setPosts((prev) =>
        prev.map((p) => (p.id === updated.id ? { ...p, ...updated } : p))
      );
      fetchPinned();
    },
    [fetchPinned]
  );

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  const title = isHome ? "Derniers articles" : "Tous les articles";

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>{isHome ? "NICKORP" : title}</title>
        <meta
          name="description"
          content={
            isHome
              ? "D\u00e9couvrez les derniers articles de notre blog."
              : "Liste compl\u00e8te des articles du blog."
          }
        />
      </Helmet>
      {isHome && pinnedPosts.length > 0 && (
        <FeaturedPosts posts={pinnedPosts} />
      )}

      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
        {!isHome && (
          <Link
            to="/"
            className="text-sm text-gray-500 hover:text-black transition-colors"
          >
            Retour
          </Link>
        )}
      </div>

      {posts.length > 0 ? (
        <>
          <div>
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onChange={handlePostChange}
              />
            ))}
          </div>

          {isHome && showFullListLink && (
            <div className="mt-8 text-center">
              <Link
                to="/articles"
                className="text-sm text-gray-500 hover:text-black transition-colors"
              >
                Voir tous les articles
              </Link>
            </div>
          )}

          {!isHome && (
            <Pagination
              page={page}
              totalPages={totalPages}
              setSearchParams={setSearchParams}
            />
          )}
        </>
      ) : (
        <p className="text-gray-500 text-center mt-12">
          Aucun article pour le moment.
        </p>
      )}
    </div>
  );
}
