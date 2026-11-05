/* Minimal API client for the NightOut AI backend.
   Phase 1: only /api/health is called. Generation endpoints arrive in Phase 2+. */

const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request(path, options = {}, timeoutMs = 10000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
      signal: controller.signal,
    });
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const body = await res.json();
        if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      } catch {
        /* non-JSON error body — keep the status text */
      }
      throw new Error(detail);
    }
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  async health() {
    return request("/api/health");
  },
  // Phase 3 wires this to real generation; kept here so the frontend contract is stable.
  async generateNight(payload) {
    return request("/api/generate", { method: "POST", body: JSON.stringify(payload) });
  },
};
