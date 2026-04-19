import { Helmet } from "react-helmet-async";

export default function Contact() {
  return (
    <div className="max-w-[760px] mx-auto px-5 sm:px-10 py-12 lg:py-16">
      <Helmet>
        <title>Contact &mdash; NICKORP</title>
        <meta
          name="description"
          content="Contactez NICKORP &mdash; retrouvez-nous sur GitHub et LinkedIn."
        />
      </Helmet>

      <p
        className="font-sans text-editorial-accent font-semibold mb-3"
        style={{
          fontSize: 11,
          letterSpacing: 2,
          textTransform: "uppercase",
        }}
      >
        Échanger
      </p>

      <h1
        className="font-serif text-editorial-ink"
        style={{
          fontSize: "clamp(32px, 4.6vw, 54px)",
          lineHeight: 1.05,
          fontWeight: 600,
          letterSpacing: "-0.02em",
          margin: "0 0 28px",
        }}
      >
        Contact
      </h1>

      <p
        className="font-serif text-editorial-dim italic"
        style={{
          fontSize: "clamp(17px, 2vw, 22px)",
          lineHeight: 1.4,
          margin: "0 0 40px",
          maxWidth: 560,
        }}
      >
        Une question, une suggestion, ou simplement envie de continuer la
        conversation ailleurs.
      </p>

      <ul className="border-t border-editorial-rule">
        <li className="border-b border-editorial-rule">
          <a
            href="https://github.com/nicolasdeclerck/"
            target="_blank"
            rel="noopener noreferrer"
            className="group flex items-baseline justify-between py-5 hover:bg-editorial-rule2 -mx-3 px-3 transition-colors"
          >
            <span>
              <span
                className="block text-editorial-dim font-sans"
                style={{
                  fontSize: 11,
                  letterSpacing: 1.3,
                  textTransform: "uppercase",
                  fontWeight: 500,
                  marginBottom: 4,
                }}
              >
                Code
              </span>
              <span className="font-serif text-editorial-ink2 text-xl">
                GitHub &mdash; nicolasdeclerck
              </span>
            </span>
            <span
              className="text-editorial-accent font-sans text-sm group-hover:translate-x-1 transition-transform"
              aria-hidden
            >
              →
            </span>
          </a>
        </li>
        <li className="border-b border-editorial-rule">
          <a
            href="https://www.linkedin.com/in/nicolas-declerck/"
            target="_blank"
            rel="noopener noreferrer"
            className="group flex items-baseline justify-between py-5 hover:bg-editorial-rule2 -mx-3 px-3 transition-colors"
          >
            <span>
              <span
                className="block text-editorial-dim font-sans"
                style={{
                  fontSize: 11,
                  letterSpacing: 1.3,
                  textTransform: "uppercase",
                  fontWeight: 500,
                  marginBottom: 4,
                }}
              >
                Pro
              </span>
              <span className="font-serif text-editorial-ink2 text-xl">
                LinkedIn &mdash; Nicolas Declerck
              </span>
            </span>
            <span
              className="text-editorial-accent font-sans text-sm group-hover:translate-x-1 transition-transform"
              aria-hidden
            >
              →
            </span>
          </a>
        </li>
      </ul>
    </div>
  );
}
