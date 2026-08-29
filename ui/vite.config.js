import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev mode the Vite server proxies API calls to the FastAPI backend
// (start it with: uv run uvicorn app.main:app --port 8000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/tasks": "http://localhost:8000",
      "/categories": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
