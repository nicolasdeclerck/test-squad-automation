export default function LinkedInShareButton({ title, status }) {
  if (status !== "published") return null;

  const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
    window.location.origin + window.location.pathname,
  )}`;

  return (
    <div
      style={{
        marginTop: 56,
        display: "flex",
        alignItems: "center",
        gap: 12,
        flexWrap: "wrap",
        fontFamily: '"Inter", system-ui, sans-serif',
      }}
    >
      <span
        style={{
          fontSize: 11,
          color: "rgb(var(--color-editorial-dim))",
          textTransform: "uppercase",
          letterSpacing: 1,
          fontWeight: 500,
        }}
      >
        Partager
      </span>
      <a
        href={shareUrl}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Partager « ${title} » sur LinkedIn`}
        title="Partager sur LinkedIn"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          fontSize: 12,
          fontWeight: 500,
          padding: "6px 10px",
          borderRadius: 3,
          textDecoration: "none",
          border: "1px solid rgb(var(--color-editorial-rule))",
          background: "rgb(var(--color-editorial-card))",
          color: "rgb(var(--color-editorial-text))",
        }}
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.852 3.37-1.852 3.601 0 4.267 2.37 4.267 5.455v6.288zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.063 2.063 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
        </svg>
        <span>LinkedIn</span>
      </a>
    </div>
  );
}
