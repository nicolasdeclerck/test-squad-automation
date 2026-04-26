import { describe, expect, it } from "vitest";

import { buildHeadingIndex, slugify } from "./articleToc";

describe("slugify", () => {
  it("returns an empty string for null, undefined or empty input", () => {
    expect(slugify("")).toBe("");
    expect(slugify(null)).toBe("");
    expect(slugify(undefined)).toBe("");
  });

  it("lowercases the input and replaces spaces with dashes", () => {
    expect(slugify("Hello World")).toBe("hello-world");
  });

  it("strips diacritics from accented characters", () => {
    expect(slugify("Éléphant à Noël")).toBe("elephant-a-noel");
  });

  it("removes special characters", () => {
    expect(slugify("C'est génial !")).toBe("cest-genial");
  });

  it("collapses consecutive spaces and dashes", () => {
    expect(slugify("  Foo   --  bar  ")).toBe("foo-bar");
  });

  it("trims leading and trailing dashes", () => {
    expect(slugify("---hello---")).toBe("hello");
  });
});

describe("buildHeadingIndex", () => {
  it("returns empty items and preserves input when html is empty", () => {
    expect(buildHeadingIndex("")).toEqual({ items: [], html: "" });
    expect(buildHeadingIndex(null)).toEqual({ items: [], html: "" });
  });

  it("extracts h1, h2 and h3 headings with text, id and level", () => {
    const html =
      "<h1>Introduction</h1><p>intro</p><h2>Contexte</h2><h3>Détails</h3>";
    const { items } = buildHeadingIndex(html);

    expect(items).toEqual([
      { id: "introduction", text: "Introduction", level: 1 },
      { id: "contexte", text: "Contexte", level: 2 },
      { id: "details", text: "Détails", level: 3 },
    ]);
  });

  it("ignores headings with empty text content", () => {
    const html = "<h1></h1><h2>   </h2><h2>Visible</h2>";
    const { items } = buildHeadingIndex(html);

    expect(items).toHaveLength(1);
    expect(items[0].text).toBe("Visible");
  });

  it("disambiguates colliding slugs with a numeric suffix", () => {
    const html = "<h2>Section</h2><h2>Section</h2><h2>Section</h2>";
    const { items } = buildHeadingIndex(html);

    expect(items.map((item) => item.id)).toEqual([
      "section",
      "section-2",
      "section-3",
    ]);
  });

  it("falls back to 'section' when the heading slug is empty", () => {
    const html = "<h2>!!!</h2><h2>???</h2>";
    const { items } = buildHeadingIndex(html);

    expect(items.map((item) => item.id)).toEqual(["section", "section-2"]);
  });

  it("injects the generated id on the corresponding heading in the returned html", () => {
    const html = "<h1>Bonjour</h1><p>texte</p>";
    const { html: output } = buildHeadingIndex(html);

    expect(output).toContain('id="bonjour"');
    expect(output).toContain("<p>texte</p>");
  });

  it("ignores headings deeper than h3", () => {
    const html = "<h1>Top</h1><h4>Sub</h4><h5>Sub</h5>";
    const { items } = buildHeadingIndex(html);

    expect(items.map((item) => item.level)).toEqual([1]);
  });
});
