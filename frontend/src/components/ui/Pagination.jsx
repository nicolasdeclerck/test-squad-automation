import { useSearchParams } from "react-router-dom";

export default function Pagination({ page, totalPages }) {
  const [, setSearchParams] = useSearchParams();

  if (totalPages <= 1) return null;

  return (
    <div className="mt-8 flex items-center justify-center gap-4">
      {page > 1 && (
        <button
          onClick={() => setSearchParams({ page: page - 1 })}
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          &larr; Pr&eacute;c&eacute;dent
        </button>
      )}
      <span className="text-sm text-gray-400">
        Page {page} sur {totalPages}
      </span>
      {page < totalPages && (
        <button
          onClick={() => setSearchParams({ page: page + 1 })}
          className="text-sm text-gray-500 hover:text-black transition-colors"
        >
          Suivant &rarr;
        </button>
      )}
    </div>
  );
}
