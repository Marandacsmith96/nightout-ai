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

/* Random-but-sensible "Surprise Me" plan — lets the app create an itinerary
   without requiring any other input (Phase 5). */
export const SURPRISE_CITIES = [
  { city: "Denver", state: "CO" },
  { city: "Boulder", state: "CO" },
  { city: "Austin", state: "TX" },
];

export function randomSurprisePlan() {
  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const base = pick(SURPRISE_CITIES);
  const activities = ["Dinner"];
  const extras = ["Games & arcade bars", "Casual drinks", "Live music", "Dancing", "Escape rooms", "Dessert or coffee", "Comedy shows"].filter(
    (a) => a !== "Dinner"
  );
  // shuffle extras, take 2
  for (let i = extras.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [extras[i], extras[j]] = [extras[j], extras[i]];
  }
  activities.push(...extras.slice(0, 2));

  const saturday = new Date();
  const day = saturday.getDay();
  const diff = (6 - day + 7) % 7 || 7; // next Saturday (or a week out)
  saturday.setDate(saturday.getDate() + diff);

  return {
    city: base.city,
    state: base.state,
    date: saturday.toISOString().slice(0, 10),
    groupSize: 2 + Math.floor(Math.random() * 6),
    budget: pick([30, 60, 100]),
    startTime: "19:00",
    endTime: pick(["22:30", "23:30", "00:30"]),
    restrictions: [],
    activities,
    atmosphere: "Surprise me",
    transport: "Walking",
    distance: "Moderate travel between stops is okay",
    notes: "Surprise us! Pick great spots we didn't think of.",
  };
}

export function formatTime(t) {
  if (!t) return "—";
  const [h, m] = t.split(":").map(Number);
  const ampm = h >= 12 ? "PM" : "AM";
  const hh = h % 12 === 0 ? 12 : h % 12;
  return `${hh}:${String(m).padStart(2, "0")} ${ampm}`;
}
