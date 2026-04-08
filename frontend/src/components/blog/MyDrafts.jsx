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
      <div className="max-w-3xl mx-auto px-4 py-12">
        <p className="text-gray-500 text-center">Chargement...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Helmet>
        <title>Mes brouillons</title>
        <meta name="description" content="Liste de vos articles en brouillon." />
      </Helmet>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Mes brouillons</h1>
        <Link
          to="/articles"
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          Retour
        </Link>
      </div>

      {posts.length > 0 ? (
        <>
          <div>
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
        <p className="text-gray-500 text-center mt-12">
          Aucun brouillon pour le moment.
        </p>
      )}
    </div>
  );
}
