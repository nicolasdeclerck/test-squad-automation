import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import Pagination from "../ui/Pagination";
import PostCard from "./PostCard";

export default function MyDrafts() {
  const [posts, setPosts] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1", 10);

  useEffect(() => {
    setLoading(true);
    api.get(`/api/blog/posts/?status=draft&page=${page}`).then((res) => {
      if (res.ok) {
        setPosts(res.data.results);
        setTotalPages(Math.ceil(res.data.count / 10));
      }
      setLoading(false);
    });
  }, [page]);

  if (loading) {
    return (
      <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-12">
        <p className="text-editorial-dim text-center">Chargement…</p>
      </div>
    );
  }

  return (
    <div className="max-w-[1200px] mx-auto px-5 sm:px-10 py-12 lg:py-16">
      <Helmet>
        <title>Mes brouillons</title>
        <meta name="description" content="Liste de vos articles en brouillon." />
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
          Auteur
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
            Mes brouillons
          </h1>
          <Link
            to="/"
            className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors shrink-0 pb-2"
          >
            ← Retour
          </Link>
        </div>
      </div>

      <div className="max-w-[760px]">
        {posts.length > 0 ? (
          <>
            <div className="border-t border-editorial-rule">
              {posts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
            <Pagination
              page={page}
              totalPages={totalPages}
              setSearchParams={setSearchParams}
            />
          </>
        ) : (
          <p className="font-serif italic text-editorial-dim text-lg mt-12">
            Aucun brouillon pour le moment.
          </p>
        )}
      </div>
    </div>
  );
}
