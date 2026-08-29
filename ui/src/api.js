// Thin fetch wrapper around the REST API.
// In dev, Vite proxies /tasks and /categories to the FastAPI backend.
// In production, FastAPI serves this UI from the same origin.

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body.detail) detail = typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail);
    } catch {
      // ignore body parse errors
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Tasks
  listTasks(params = {}) {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== null && v !== undefined && v !== "") qs.set(k, v);
    }
    const s = qs.toString();
    return request(`/tasks${s ? `?${s}` : ""}`);
  },
  createTask(data) {
    return request("/tasks", { method: "POST", body: JSON.stringify(data) });
  },
  updateTask(id, data) {
    return request(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  deleteTask(id) {
    return request(`/tasks/${id}`, { method: "DELETE" });
  },

  // Categories
  listCategories() {
    return request("/categories?page_size=100");
  },
  createCategory(data) {
    return request("/categories", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  deleteCategory(id) {
    return request(`/categories/${id}`, { method: "DELETE" });
  },
};
