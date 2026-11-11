/* Minimal API client for the NightOut AI backend. */
import { toApiPlan } from "../lib/apiPlan.js";

const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) {
        const first = Array.isArray(body.detail) ? body.detail[0] : body.detail;
        detail = first?.msg ? `${first.msg} — ${first.loc?.[1] ?? "field"}` : String(first);
      }
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  async health() {
    return request("/api/health");
  },
  async generateNight(payload) {
    return request("/api/plan/generate", {
      method: "POST",
      body: JSON.stringify(toApiPlan(payload)),
    });
  },
  // Phase 4: conversational edits + locked regeneration.
  // NOTE: the destructured plan is renamed to `plan` — naming it `request`
  // shadowed the module-level request() helper and broke every edit in the
  // browser (TypeError: request is not a function). Found during QA
  // click-through; see BUILD_LOG Phase 8.
  async editNight({ instruction, request: plan, itinerary, lockedIndices }) {
    return request("/api/plan/edit", {
      method: "POST",
      body: JSON.stringify({
        instruction,
        request: toApiPlan(plan),
        itinerary,
        locked_indices: lockedIndices ?? [],
      }),
    });
  },
  // Phase 7: multimodal media (promo poster + voice-over).
  async poster(itinerary) {
    return request("/api/media/poster", {
      method: "POST",
      body: JSON.stringify(itinerary),
    });
  },
  async voiceover(itinerary) {
    return request("/api/media/voiceover", {
      method: "POST",
      body: JSON.stringify(itinerary),
    });
  },
};
