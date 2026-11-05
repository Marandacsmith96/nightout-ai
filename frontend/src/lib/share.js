/* Save / share helpers for itineraries.
   - localStorage holds the user's saved nights.
   - A share link packs {plan, itinerary} into the URL fragment (no server
     needed); long links may be trimmed by some chat apps, so the formatted
     text copy is the reliable path for group chats. */

import { formatTime } from "../lib/nightOptions.js";

const SAVED_KEY = "nightout-saved";
const KIND_LABEL = {
  dinner: "Dinner",
  "cocktail bars": "Cocktails",
  "casual drinks": "Casual drinks",
  "live music": "Live music",
  dancing: "Dancing",
  "comedy shows": "Comedy",
  concerts: "Concert",
  "games & arcade bars": "Games & arcade",
  bowling: "Bowling",
  "escape rooms": "Escape room",
  "outdoor activities": "Outdoors",
  "dessert or coffee": "Dessert / coffee",
  "something unexpected": "Something unexpected",
};

export function loadSaved() {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) || "[]");
  } catch {
    return [];
  }
}

export function saveNight({ plan, itinerary }) {
  const list = loadSaved().filter((s) => s.itinerary?.id !== itinerary.id);
  list.unshift({
    savedAt: new Date().toISOString(),
    label: `${itinerary.city} · ${new Date(itinerary.date).toLocaleDateString()}`,
    plan,
    itinerary,
  });
  localStorage.setItem(SAVED_KEY, JSON.stringify(list.slice(0, 20)));
  return list;
}

export function deleteSaved(id) {
  const list = loadSaved().filter((s) => s.itinerary?.id !== id);
  localStorage.setItem(SAVED_KEY, JSON.stringify(list));
  return list;
}

export function encodeShare({ plan, itinerary }) {
  const json = JSON.stringify({ plan, itinerary });
  return btoa(unescape(encodeURIComponent(json)));
}

export function decodeShare(hash) {
  try {
    const data = JSON.parse(decodeURIComponent(escape(atob(hash))));
    if (data?.itinerary) return data;
  } catch {
    /* malformed link — ignore */
  }
  return null;
}

export function itineraryText(it) {
  const lines = [];
  lines.push(`🌙 NIGHTOUT AI — ${it.city}`);
  lines.push(
    `${new Date(it.date).toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })} · ${it.stops.length} stop(s)`
  );
  lines.push("");
  it.stops.forEach((s, i) => {
    lines.push(
      `${i + 1}. ${KIND_LABEL[s.kind] || s.kind} — ${s.title} (${formatTime(s.start)}–${formatTime(s.end)})`
    );
    lines.push(`   ${s.venue?.address || ""}`);
    if (s.cost_per_person != null) lines.push(`   ~$${s.cost_per_person}/person`);
    if (s.note) lines.push(`   ${s.note}`);
    if (s.venue?.google_maps_url) lines.push(`   ${s.venue.google_maps_url.replace(/&amp;/g, "&")}`);
    lines.push("");
  });
  const ok = it.demo ? "Sample places (demo mode)" : "";
  lines.push(
    `💰 Est. ${it.budget.per_person_total}/${it.budget.budget} per person · group-friendly`
  );
  if (ok) lines.push(`🧪 ${ok}`);
  if (!it.demo) lines.push(`Planned with NightOut AI`);
  return lines.join("\n");
}

export async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return true;
  }
  // Fallback for non-secure contexts
  const ta = document.createElement("textarea");
  ta.value = text;
  document.body.appendChild(ta);
  ta.select();
  const ok = document.execCommand("copy");
  ta.remove();
  return ok;
}
