const INDENT_BY_LEVEL = { 1: 0, 2: 12, 3: 24 };

const SUMMARY_LABEL_STYLE = {
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: 2,
  textTransform: "uppercase",
  color: "rgb(var(--color-editorial-dim))",
};

function Chevron() {
  return (
    <svg
      width="10"
      height="10"
      viewBox="0 0 12 12"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{ transition: "transform 150ms ease" }}
      className="article-toc-chevron"
    >
      <path d="m3 4.5 3 3 3-3" />
    </svg>
  );
}

export default function ArticleToc({ items, collapsible = false }) {
  if (!Array.isArray(items) || items.length < 2) return null;

  const handleClick = (event, id) => {
    event.preventDefault();
    const target = document.getElementById(id);
    if (!target) return;
    const details = event.currentTarget.closest("details");
    if (details) details.open = false;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    if (window.history?.replaceState) {
      window.history.replaceState(null, "", `#${id}`);
    }
  };

  const list = (
    <ol style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {items.map((item) => (
        <li
          key={item.id}
          style={{
            paddingLeft: INDENT_BY_LEVEL[item.level] ?? 0,
            lineHeight: 1.5,
            margin: "4px 0",
          }}
        >
          <a
            href={`#${item.id}`}
            onClick={(event) => handleClick(event, item.id)}
            style={{
              fontSize: item.level === 1 ? 14 : 13,
              fontWeight: item.level === 1 ? 500 : 400,
              color: "rgb(var(--color-editorial-ink2))",
              textDecoration: "none",
              borderBottom: "1px solid transparent",
              transition: "border-color 120ms ease, color 120ms ease",
            }}
            onMouseEnter={(event) => {
              event.currentTarget.style.borderBottomColor =
                "rgb(var(--color-editorial-ink2))";
            }}
            onMouseLeave={(event) => {
              event.currentTarget.style.borderBottomColor = "transparent";
            }}
          >
            {item.text}
          </a>
        </li>
      ))}
    </ol>
  );

  if (collapsible) {
    return (
      <details
        className="article-toc-details"
        open
        style={{
          fontFamily: '"Inter", system-ui, sans-serif',
          border: "1px solid rgb(var(--color-editorial-rule))",
          borderRadius: 3,
          padding: "14px 18px",
          background: "rgb(var(--color-editorial-card))",
        }}
      >
        <summary
          style={{
            ...SUMMARY_LABEL_STYLE,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
            cursor: "pointer",
            listStyle: "none",
          }}
          aria-label="Sommaire de l'article"
        >
          <span>Sommaire</span>
          <Chevron />
        </summary>
        <div style={{ marginTop: 12 }}>{list}</div>
      </details>
    );
  }

  return (
    <nav
      aria-label="Sommaire de l'article"
      style={{
        fontFamily: '"Inter", system-ui, sans-serif',
        margin: "0 0 40px",
        padding: "20px 0",
        background: "rgb(var(--color-editorial-paper))",
      }}
    >
      <h2 style={{ ...SUMMARY_LABEL_STYLE, margin: "0 0 14px" }}>Sommaire</h2>
      {list}
    </nav>
  );
}
