function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

async function fetchCSRF() {
  if (!getCookie("csrftoken")) {
    await fetch("/api/accounts/csrf/", { credentials: "include" });
  }
  return getCookie("csrftoken");
}

async function apiRequest(url, options = {}) {
  const config = {
    credentials: "include",
    headers: {
      ...(options.headers || {}),
    },
    ...options,
  };

  if (["POST", "PUT", "PATCH", "DELETE"].includes(config.method)) {
    const csrfToken = await fetchCSRF();
    config.headers["X-CSRFToken"] = csrfToken;
  }

  if (!(config.body instanceof FormData) && config.body) {
    config.headers["Content-Type"] = "application/json";
    if (typeof config.body === "object") {
      config.body = JSON.stringify(config.body);
    }
  }

  const response = await fetch(url, config);

  if (response.status === 204) {
    return { ok: true, data: null };
  }

  let data;
  try {
    data = await response.json();
  } catch {
    return { ok: false, errors: { detail: "Erreur serveur" }, status: response.status };
  }

  if (!response.ok) {
    return { ok: false, errors: data, status: response.status };
  }

  return { ok: true, data };
}

export const api = {
  get: (url) => apiRequest(url),
  post: (url, body) => apiRequest(url, { method: "POST", body }),
  put: (url, body) => apiRequest(url, { method: "PUT", body }),
  patch: (url, body) => apiRequest(url, { method: "PATCH", body }),
  delete: (url) => apiRequest(url, { method: "DELETE" }),
};
