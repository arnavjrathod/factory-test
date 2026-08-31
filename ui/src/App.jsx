import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api.js";

const STATUSES = ["todo", "in_progress", "done"];
const PRIORITIES = ["low", "medium", "high"];

function statusBadge(s) {
  return `badge status-${s}`;
}

function formatDate(iso) {
  if (!iso) return null;
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function TaskItem({ task, category, onToggle, onEdit, onDelete }) {
  const done = task.status === "done";
  return (
    <li className={`task ${done ? "done" : ""}`}>
      <input
        type="checkbox"
        className="check"
        checked={done}
        onChange={() => onToggle(task)}
        aria-label={`Mark "${task.title}" as ${done ? "todo" : "done"}`}
      />
      <div className="body">
        <div className="title">{task.title}</div>
        {task.description && <div className="desc">{task.description}</div>}
        <div className="meta">
          <span className={statusBadge(task.status)}>
            {task.status.replace("_", " ")}
          </span>
          <span className={`badge priority-${task.priority}`}>
            {task.priority}
          </span>
          {category && <span className="badge">{category.name}</span>}
          {task.due_date && (
            <span
              className={`badge due ${task.overdue ? "overdue" : ""}`}
              title={task.overdue ? "Overdue" : "Due date"}
            >
              {task.overdue ? "⚠ " : "📅 "}
              {formatDate(task.due_date)}
            </span>
          )}
        </div>
      </div>
      <div className="actions">
        <button className="ghost" onClick={() => onEdit(task)} title="Edit">
          ✏️
        </button>
        <button
          className="ghost danger"
          onClick={() => onDelete(task)}
          title="Delete"
        >
          🗑
        </button>
      </div>
    </li>
  );
}

function TaskForm({ initial, categories, onSubmit, onCancel }) {
  const editing = Boolean(initial);
  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [status, setStatus] = useState(initial?.status ?? "todo");
  const [priority, setPriority] = useState(initial?.priority ?? "medium");
  const [dueDate, setDueDate] = useState(initial?.due_date ?? "");
  const [categoryId, setCategoryId] = useState(initial?.category_id ?? "");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) {
      setError("Title is required");
      return;
    }
    setBusy(true);
    setError(null);
    const data = {
      title: title.trim(),
      description: description.trim() || null,
      status,
      priority,
      due_date: dueDate || null,
      category_id: categoryId ? Number(categoryId) : null,
    };
    try {
      await onSubmit(data);
      if (!editing) {
        setTitle("");
        setDescription("");
        setStatus("todo");
        setPriority("medium");
        setDueDate("");
        setCategoryId("");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="task-form card" onSubmit={handleSubmit}>
      <input
        className="grow"
        placeholder="What needs to be done?"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <input
        className="grow"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {editing && (
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace("_", " ")}
            </option>
          ))}
        </select>
      )}
      <select value={priority} onChange={(e) => setPriority(e.target.value)}>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <select
        value={categoryId}
        onChange={(e) => setCategoryId(e.target.value)}
      >
        <option value="">No category</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <input
        type="date"
        value={dueDate ?? ""}
        onChange={(e) => setDueDate(e.target.value)}
      />
      <button type="submit" disabled={busy}>
        {busy ? "Saving…" : editing ? "Save" : "Add task"}
      </button>
      {editing && (
        <button type="button" className="secondary" onClick={onCancel}>
          Cancel
        </button>
      )}
      {error && (
        <div className="error">
          {error}
        </div>
      )}
    </form>
  );
}

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [categories, setCategories] = useState([]);

  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [sort, setSort] = useState("");
  const [order, setOrder] = useState("asc");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null);
  const [newCategory, setNewCategory] = useState("");

  const categoryById = useMemo(() => {
    const map = new Map();
    for (const c of categories) map.set(c.id, c);
    return map;
  }, [categories]);

  const loadTasks = useCallback(async () => {
    try {
      const data = await api.listTasks({
        status,
        priority,
        category_id: categoryId,
        sort,
        order,
        page,
        page_size: pageSize,
      });
      setTasks(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages || 1);
      setError(null);
    } catch (err) {
      setError(`Failed to load tasks: ${err.message}`);
    }
  }, [status, priority, categoryId, sort, order, page]);

  const loadCategories = useCallback(async () => {
    try {
      const data = await api.listCategories();
      setCategories(data.items);
    } catch (err) {
      setError(`Failed to load categories: ${err.message}`);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  // Reset to page 1 whenever filters change.
  useEffect(() => {
    setPage(1);
  }, [status, priority, categoryId, sort, order]);

  async function handleCreateTask(data) {
    await api.createTask(data);
    await loadTasks();
    await loadCategories();
  }

  async function handleUpdateTask(data) {
    await api.updateTask(editing.id, data);
    setEditing(null);
    await loadTasks();
  }

  async function handleToggle(task) {
    const next = task.status === "done" ? "todo" : "done";
    setTasks((ts) =>
      ts.map((t) => (t.id === task.id ? { ...t, status: next } : t))
    );
    try {
      await api.updateTask(task.id, { status: next });
      await loadTasks();
    } catch (err) {
      setError(err.message);
      await loadTasks();
    }
  }

  async function handleDelete(task) {
    if (!window.confirm(`Delete "${task.title}"?`)) return;
    try {
      await api.deleteTask(task.id);
      await loadTasks();
      await loadCategories();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAddCategory(e) {
    e.preventDefault();
    const name = newCategory.trim();
    if (!name) return;
    try {
      await api.createCategory({ name });
      setNewCategory("");
      await loadCategories();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteCategory(cat) {
    if (!window.confirm(`Delete category "${cat.name}"? Tasks will be kept.`))
      return;
    try {
      await api.deleteCategory(cat.id);
      if (String(cat.id) === categoryId) setCategoryId("");
      await loadCategories();
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  }

  const categoryCounts = useMemo(() => {
    const counts = new Map();
    for (const t of tasks) {
      if (t.category_id != null)
        counts.set(t.category_id, (counts.get(t.category_id) ?? 0) + 1);
    }
    return counts;
  }, [tasks]);

  return (
    <div className="container">
      <header className="app-header">
        <h1>{"// To-Do"}</h1>
        <span className="health">
          {`/* ${total} task${total === 1 ? "" : "s"} */`}
        </span>
      </header>

      {error && <div className="error">{error}</div>}

      <TaskForm
        key={editing ? `edit-${editing.id}` : "create"}
        initial={editing}
        categories={categories}
        onSubmit={editing ? handleUpdateTask : handleCreateTask}
        onCancel={() => setEditing(null)}
      />

      <div className="card filters">
        <label>
          Status
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace("_", " ")}
              </option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option value="">All</option>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Category
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
          >
            <option value="">All</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Sort by
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="">Created</option>
            <option value="due_date">Due date</option>
            <option value="priority">Priority</option>
          </select>
        </label>
        <label>
          Order
          <select value={order} onChange={(e) => setOrder(e.target.value)}>
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>
        </label>
        <span className="spacer" />
        <span className="result-count">
          Page {page} of {totalPages}
        </span>
      </div>

      <div className="card categories">
        <h2>Categories</h2>
        {categories.length === 0 ? (
          <div className="empty">
            No categories yet.
          </div>
        ) : (
          <ul>
            {categories.map((c) => (
              <li key={c.id}>
                <span className="name">
                  {c.name}
                  <span className="count">({categoryCounts.get(c.id) ?? 0} on this page)</span>
                </span>
                <button
                  className="ghost danger"
                  onClick={() => handleDeleteCategory(c)}
                  title="Delete category"
                >
                  🗑
                </button>
              </li>
            ))}
          </ul>
        )}
        <form onSubmit={handleAddCategory}>
          <input
            placeholder="New category name"
            value={newCategory}
            onChange={(e) => setNewCategory(e.target.value)}
          />
          <button type="submit" className="secondary">
            Add
          </button>
        </form>
      </div>

      {tasks.length === 0 ? (
        <div className="empty card">
          Nothing here. Add your first task above ☝️
        </div>
      ) : (
        <ul className="task-list">
          {tasks.map((t) => (
            <TaskItem
              key={t.id}
              task={t}
              category={categoryById.get(t.category_id)}
              onToggle={handleToggle}
              onEdit={setEditing}
              onDelete={handleDelete}
            />
          ))}
        </ul>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="secondary"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ← Prev
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            className="secondary"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
