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
      <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-12">
        <p className="text-editorial-dim text-center">Chargement…</p>
      </div>
    );
  }

  const title = isHome ? "Derniers articles" : "Tous les articles";
  const eyebrow = isHome ? "Journal" : "Archives";

  return (
    <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-12 lg:py-16">
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

      <div className="max-w-[760px]">
        <p
          className="font-sans text-editorial-accent font-semibold mb-3"
          style={{
            fontSize: 11,
            letterSpacing: 2,
            textTransform: "uppercase",
          }}
        >
          {eyebrow}
        </p>
        <div className="flex items-end justify-between gap-6 mb-12">
          <h1
            className="font-serif text-editorial-ink"
            style={{
              fontSize: "clamp(32px, 4.6vw, 54px)",
              lineHeight: 1.05,
              fontWeight: 600,
              letterSpacing: "-0.02em",
              margin: 0,
            }}
          >
            {title}
          </h1>
          {!isHome && (
            <Link
              to="/"
              className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors shrink-0 pb-2"
            >
              ← Retour
            </Link>
          )}
        </div>
      </div>

      {isHome && pinnedPosts.length > 0 && (
        <FeaturedPosts posts={pinnedPosts} />
      )}

      <div className="max-w-[760px]">
        {posts.length > 0 ? (
          <>
            <div className="border-t border-editorial-rule">
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  onChange={handlePostChange}
                />
              ))}
            </div>

            {isHome && showFullListLink && (
              <div className="mt-10 text-center">
                <Link
                  to="/articles"
                  className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
                >
                  Voir tous les articles →
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
          <p className="text-editorial-dim text-center mt-12 italic">
            Aucun article pour le moment.
          </p>
        )}
      </div>
    </div>
  );
}
