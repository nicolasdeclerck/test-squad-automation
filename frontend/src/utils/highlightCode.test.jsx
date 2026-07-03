import { render, waitFor } from "@testing-library/react";
import { useRef } from "react";

import { useSyntaxHighlight } from "./highlightCode";

function Harness({ html }) {
  const ref = useRef(null);
  useSyntaxHighlight(ref, html);
  return <div ref={ref} dangerouslySetInnerHTML={{ __html: html }} />;
}

const codeBlock = (language, code) =>
  `<pre><code class="bn-inline-content language-${language}">${code}</code></pre>`;

describe("useSyntaxHighlight", () => {
  it("highlights code blocks tagged with a supported language", async () => {
    const { container } = render(
      <Harness html={codeBlock("javascript", "const answer = 42;")} />,
    );

    await waitFor(() => {
      const code = container.querySelector("pre code");
      expect(code.classList.contains("hljs")).toBe(true);
    });

    expect(container.querySelector(".hljs-keyword")).not.toBeNull();
  });

  it("leaves plain-text blocks untouched", async () => {
    const html = codeBlock("text", "just some text");
    const { container } = render(<Harness html={html} />);

    // Give the lazy highlighter a chance to run before asserting nothing happened.
    await new Promise((resolve) => setTimeout(resolve, 20));

    const code = container.querySelector("pre code");
    expect(code.classList.contains("hljs")).toBe(false);
    expect(code.textContent).toBe("just some text");
  });

  it("leaves unknown languages as plain code without warnings", async () => {
    const html = codeBlock("some-unknown-lang", "mystery content");
    const { container } = render(<Harness html={html} />);

    await new Promise((resolve) => setTimeout(resolve, 20));

    const code = container.querySelector("pre code");
    expect(code.classList.contains("hljs")).toBe(false);
    expect(code.textContent).toBe("mystery content");
  });

  it("does nothing when the container has no code blocks", async () => {
    const { container } = render(<Harness html="<p>No code here</p>" />);

    await new Promise((resolve) => setTimeout(resolve, 20));

    expect(container.querySelector(".hljs")).toBeNull();
  });
});
