/* NightOut AI — option lists shared by the form and (later) the backend contract. */

export const BUDGET_PRESETS = [
  { label: "Under $30", value: 30 },
  { label: "$30–$60", value: 60 },
  { label: "$60–$100", value: 100 },
  { label: "$100–$150", value: 150 },
  { label: "$150+", value: 200 },
];

export const FOOD_RESTRICTIONS = [
  "Vegetarian",
  "Vegan",
  "Gluten-free",
  "Dairy-free",
  "Other (type below)",
];

export const ACTIVITIES = [
  "Dinner",
  "Cocktail bars",
  "Casual drinks",
  "Live music",
  "Dancing",
  "Comedy shows",
  "Concerts",
  "Games & arcade bars",
  "Bowling",
  "Escape rooms",
  "Outdoor activities",
  "Dessert or coffee",
  "Something unexpected",
];

export const ATMOSPHERES = [
  "Casual & relaxed",
  "Trendy & social",
  "Romantic",
  "Energetic nightlife",
  "Upscale",
  "Adventurous",
  "Surprise me",
];

export const TRANSPORT = ["Walking", "Driving", "Rideshare", "Public transportation"];

export const DISTANCE_PREFS = [
  "Keep everything close together",
  "Moderate travel between stops is okay",
  "Willing to travel farther for better experiences",
];

export const PRICE_LEVEL_LABEL = { 0: "unknown", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$" };

/** Human-friendly summary of the form payload (used by the live side panel). */
export function summarizeNight(p) {
  if (!p) return [];
  const rows = [
    ["City", p.city ? `${p.city}${p.state ? ", " + p.state : ""}` : "—"],
    ["Date", p.date || "—"],
    ["Group", `${p.groupSize || "—"} ${p.groupSize === 1 ? "person" : "people"}`],
    ["Budget", p.budget ? `$${p.budget}/person` : "—"],
    ["Time", p.startTime && p.endTime ? `${formatTime(p.startTime)} – ${formatTime(p.endTime)}` : "—"],
    ["Activities", p.activities?.length ? p.activities.join(", ") : "—"],
    ["Atmosphere", p.atmosphere || "—"],
    ["Getting around", p.transport || "—"],
  ];
  if (p.restrictions?.length) rows.push(["Food", p.restrictions.join(", ")]);
  return rows;
}

export function formatTime(t) {
  if (!t) return "—";
  const [h, m] = t.split(":").map(Number);
  const ampm = h >= 12 ? "PM" : "AM";
  const hh = h % 12 === 0 ? 12 : h % 12;
  return `${hh}:${String(m).padStart(2, "0")} ${ampm}`;
}
