export default function Pagination({ page, totalPages, setSearchParams }) {
  if (totalPages <= 1) return null;

  return (
    <div className="mt-12 pt-6 border-t border-editorial-rule flex items-center justify-between gap-4 font-sans">
      <div className="flex-1">
        {page > 1 && (
          <button
            onClick={() => setSearchParams({ page: page - 1 })}
            className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
          >
            ← Pr&eacute;c&eacute;dent
          </button>
        )}
      </div>
      <span
        className="text-editorial-dim2 uppercase font-semibold"
        style={{ fontSize: 11, letterSpacing: 1.6 }}
      >
        Page {page} / {totalPages}
      </span>
      <div className="flex-1 text-right">
        {page < totalPages && (
          <button
            onClick={() => setSearchParams({ page: page + 1 })}
            className="text-sm text-editorial-dim hover:text-editorial-ink transition-colors"
          >
            Suivant →
          </button>
        )}
      </div>
    </div>
  );
}
