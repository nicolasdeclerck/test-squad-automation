import React from "react";
import { createRoot } from "react-dom/client";
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine";

function BlockNoteEditorApp({ initialContent, hiddenInput }) {
  const editor = useCreateBlockNote({
    initialContent: initialContent || undefined,
    placeholders: {
      default: "Commencez à écrire votre article...",
    },
  });

  React.useEffect(() => {
    if (!hiddenInput) return;

    // Initial sync
    if (initialContent) {
      hiddenInput.value = JSON.stringify(editor.document);
    }

    // Sync on every change
    const unsubscribe = editor.onEditorContentChange(() => {
      hiddenInput.value = JSON.stringify(editor.document);
      triggerAutosave();
    });

    // Sync on form submit
    const form = hiddenInput.closest("form");
    const handleSubmit = () => {
      hiddenInput.value = JSON.stringify(editor.document);
    };
    if (form) form.addEventListener("submit", handleSubmit);

    return () => {
      unsubscribe?.();
      if (form) form.removeEventListener("submit", handleSubmit);
    };
  }, [editor, hiddenInput, initialContent]);

  return React.createElement(BlockNoteView, { editor, theme: "light" });
}

// --- Auto-save logic ---

let autosaveTimer = null;
let postSlug = null;
let isCreating = false;

function getCsrfToken() {
  const cookie = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="));
  if (cookie) return cookie.split("=")[1];
  const input = document.querySelector("[name=csrfmiddlewaretoken]");
  return input ? input.value : "";
}

function setStatus(text, type) {
  const el = document.getElementById("autosave-status");
  if (!el) return;
  el.textContent = text;
  el.className =
    "text-sm " +
    (type === "saving"
      ? "text-yellow-500"
      : type === "saved"
        ? "text-green-500"
        : type === "error"
          ? "text-red-500"
          : "text-gray-400");
}

async function createPost() {
  if (isCreating) return postSlug;
  isCreating = true;

  const form = document.getElementById("post-form");
  const titleEl = document.getElementById("id_title");
  const contentEl = document.getElementById("id_content");
  if (!form || !titleEl || !contentEl) {
    isCreating = false;
    return null;
  }

  setStatus("Sauvegarde en cours...", "saving");

  const resp = await fetch(form.dataset.createUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({
      title: titleEl.value || "Sans titre",
      content: contentEl.value || "",
    }),
  });

  if (!resp.ok) {
    setStatus("Erreur de sauvegarde", "error");
    isCreating = false;
    return null;
  }

  const data = await resp.json();
  postSlug = data.slug;

  // Update form data attributes for future autosaves
  form.dataset.postSlug = data.slug;
  form.dataset.isNew = "false";
  form.dataset.autosaveUrl = "/api/blog/posts/" + data.slug + "/autosave/";
  form.dataset.publishUrl = "/api/blog/posts/" + data.slug + "/publish/";

  // Update browser URL without reload
  const newUrl = "/articles/" + data.slug + "/modifier/";
  window.history.replaceState({}, "", newUrl);

  setStatus("Brouillon sauvegardé", "saved");
  isCreating = false;
  return data.slug;
}

async function autosave() {
  const form = document.getElementById("post-form");
  if (!form) return;

  const isNew = form.dataset.isNew === "true";
  const titleEl = document.getElementById("id_title");
  const contentEl = document.getElementById("id_content");
  if (!titleEl || !contentEl) return;

  // If new post, create it first
  if (isNew && !postSlug) {
    await createPost();
    return;
  }

  const url = form.dataset.autosaveUrl;
  if (!url) return;

  setStatus("Sauvegarde en cours...", "saving");

  try {
    const resp = await fetch(url, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        draft_title: titleEl.value,
        draft_content: contentEl.value,
      }),
    });

    if (resp.ok) {
      setStatus("Brouillon sauvegardé", "saved");
    } else {
      setStatus("Erreur de sauvegarde", "error");
    }
  } catch {
    setStatus("Erreur de sauvegarde", "error");
  }
}

function triggerAutosave() {
  if (autosaveTimer) clearTimeout(autosaveTimer);
  autosaveTimer = setTimeout(autosave, 2000);
}

// --- Publish logic ---

async function publish() {
  const form = document.getElementById("post-form");
  if (!form) return;

  // If new post not yet created, create first
  if (form.dataset.isNew === "true" && !postSlug) {
    const slug = await createPost();
    if (!slug) return;
  }

  // Auto-save first before publishing
  const titleEl = document.getElementById("id_title");
  const contentEl = document.getElementById("id_content");
  const autosaveUrl = form.dataset.autosaveUrl;

  if (autosaveUrl && titleEl && contentEl) {
    try {
      const saveResp = await fetch(autosaveUrl, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          draft_title: titleEl.value,
          draft_content: contentEl.value,
        }),
      });
      if (!saveResp.ok) {
        setStatus("Erreur de sauvegarde avant publication", "error");
        return;
      }
    } catch {
      setStatus("Erreur de sauvegarde avant publication", "error");
      return;
    }
  }

  const publishUrl = form.dataset.publishUrl;
  if (!publishUrl) return;

  try {
    const resp = await fetch(publishUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
    });

    if (resp.ok) {
      const data = await resp.json();
      window.location.href = "/articles/" + data.slug + "/";
    } else {
      const err = await resp.json();
      setStatus(err.error || "Erreur lors de la publication", "error");
    }
  } catch {
    setStatus("Erreur lors de la publication", "error");
  }
}

// --- Initialization ---

(function () {
  const container = document.getElementById("blocknote-editor");
  const hiddenInput = document.getElementById("id_content");
  if (!container || !hiddenInput) return;

  let initialContent;
  try {
    const raw = hiddenInput.value;
    if (raw) {
      initialContent = JSON.parse(raw);
    }
  } catch {
    initialContent = undefined;
  }

  const root = createRoot(container);
  root.render(
    React.createElement(BlockNoteEditorApp, { initialContent, hiddenInput })
  );

  // Title auto-save
  const titleEl = document.getElementById("id_title");
  if (titleEl) {
    titleEl.addEventListener("input", triggerAutosave);
  }

  // Intercept form submit for JS-powered publish
  const formEl = document.getElementById("post-form");
  if (formEl) {
    formEl.addEventListener("submit", function (e) {
      e.preventDefault();
      publish();
    });
  }

  // Set initial slug if editing existing post
  const form = document.getElementById("post-form");
  if (form && form.dataset.postSlug) {
    postSlug = form.dataset.postSlug;
  }
})();
