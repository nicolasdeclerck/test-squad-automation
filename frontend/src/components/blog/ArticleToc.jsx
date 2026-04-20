const INDENT_BY_LEVEL = { 1: 0, 2: 12, 3: 24 };

export default function ArticleToc({ items }) {
  if (!Array.isArray(items) || items.length < 2) return null;

  const handleClick = (event, id) => {
    event.preventDefault();
    const target = document.getElementById(id);
    if (!target) return;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    if (window.history?.replaceState) {
      window.history.replaceState(null, "", `#${id}`);
    }
  };

  return (
    <nav
      aria-label="Sommaire de l'article"
      style={{
        fontFamily: '"Inter", system-ui, sans-serif',
        margin: "48px 0 8px",
        padding: "20px 22px",
        border: "1px solid rgb(var(--color-editorial-rule))",
        background: "rgb(var(--color-editorial-card))",
        borderRadius: 3,
      }}
    >
      <h2
        style={{
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: 2,
          textTransform: "uppercase",
          color: "rgb(var(--color-editorial-dim))",
          margin: "0 0 14px",
        }}
      >
        Sommaire
      </h2>
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
    </nav>
  );
}
