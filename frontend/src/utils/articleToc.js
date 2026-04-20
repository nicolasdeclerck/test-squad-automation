export function slugify(text) {
  if (!text) return "";
  return text
    .toString()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function buildHeadingIndex(html) {
  if (!html || typeof DOMParser === "undefined") {
    return { items: [], html: html || "" };
  }

  const doc = new DOMParser().parseFromString(html, "text/html");
  const nodes = doc.body.querySelectorAll("h1, h2, h3");
  const used = new Map();
  const items = [];

  nodes.forEach((node) => {
    const text = (node.textContent || "").trim();
    if (!text) return;
    const base = slugify(text) || "section";
    const count = used.get(base) ?? 0;
    const id = count === 0 ? base : `${base}-${count + 1}`;
    used.set(base, count + 1);
    node.id = id;
    items.push({
      id,
      text,
      level: Number(node.tagName.substring(1)),
    });
  });

  return { items, html: doc.body.innerHTML };
}
