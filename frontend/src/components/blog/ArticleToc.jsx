import { useState } from "react";

const INDENT_BY_LEVEL = { 1: "pl-0", 2: "pl-3", 3: "pl-6" };

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
      className="article-toc-chevron transition-transform duration-150"
    >
      <path d="m3 4.5 3 3 3-3" />
    </svg>
  );
}

export default function ArticleToc({ items, collapsible = false }) {
  const [open, setOpen] = useState(true);

  if (!Array.isArray(items) || items.length < 2) return null;

  const handleClick = (event, id) => {
    event.preventDefault();
    const target = document.getElementById(id);
    if (!target) return;
    if (collapsible) setOpen(false);
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    if (window.history?.replaceState) {
      window.history.replaceState(null, "", `#${id}`);
    }
  };

  const list = (
    <ol className="list-none p-0 m-0">
      {items.map((item) => (
        <li
          key={item.id}
          className={`${INDENT_BY_LEVEL[item.level] ?? "pl-0"} my-1 leading-6`}
        >
          <a
            href={`#${item.id}`}
            onClick={(event) => handleClick(event, item.id)}
            className={`article-toc-link no-underline text-editorial-ink2 ${
              item.level === 1
                ? "text-sm font-medium"
                : "text-[13px] font-normal"
            }`}
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
        className="article-toc-details font-sans border border-editorial-rule rounded-[3px] px-[18px] py-[14px] bg-editorial-card"
        open={open}
        onToggle={(event) => setOpen(event.currentTarget.open)}
      >
        <summary
          className="article-toc-label flex items-center justify-between gap-2 cursor-pointer list-none"
          aria-label="Sommaire de l'article"
        >
          <span>Sommaire</span>
          <Chevron />
        </summary>
        <div className="mt-3">{list}</div>
      </details>
    );
  }

  return (
    <nav
      aria-label="Sommaire de l'article"
      className="font-sans my-0 mb-10 py-5 bg-editorial-paper"
    >
      <h2 className="article-toc-label mt-0 mb-[14px]">Sommaire</h2>
      {list}
    </nav>
  );
}
