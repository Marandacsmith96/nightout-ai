import { Button, LoadingOverlay } from "./kit.jsx";
import { formatTime } from "../lib/nightOptions.js";
import "../itinerary.css";

const KIND_LABEL = {
  dinner: "🍽️ Dinner",
  "cocktail bars": "🍸 Cocktails",
  "casual drinks": "🍺 Casual drinks",
  "live music": "🎸 Live music",
  dancing: "🕺 Dancing",
  "comedy shows": "🎤 Comedy",
  concerts: "🎫 Concert",
  "games & arcade bars": "🕹️ Games & arcade",
  bowling: "🎳 Bowling",
  "escape rooms": "🔐 Escape room",
  "outdoor activities": "🌳 Outdoors",
  "dessert or coffee": "🍨 Dessert / coffee",
  "something unexpected": "✨ Something unexpected",
};

export default function ItineraryView({ itinerary, onRegenerate, busy, onSwap, lockedIndices = [], onToggleLock }) {
  const demo = itinerary?.demo;
  return (
    <section className="itinerary">
      {busy ? <LoadingOverlay title="Rebuilding your night…" /> : null}
      <div className="itin-header">
        <div>
          <h2>
            Your {itinerary.city} Night Out{" "}
            {demo ? <span className="demo-chip">🧪 sample places</span> : null}
          </h2>
          <div className="itin-meta">
            {new Date(itinerary.date).toLocaleDateString(undefined, {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}{" "}
            · {itinerary.stops.length} stop{itinerary.stops.length === 1 ? "" : "s"}
          </div>
        </div>
        <Button variant="ghost" onClick={onRegenerate}>
          🎲 Regenerate
        </Button>
      </div>

      <div className="timeline">
        {itinerary.stops.map((stop, i) => {
          const v = stop.venue;
          const mapsUrl = v?.google_maps_url?.replace(/&amp;/g, "&");
          const locked = lockedIndices.includes(i);
          return (
            <div key={stop.index} className="stop">
              <div className="stop-dot">{i + 1}</div>
              <div className="stop-card">
                <div className="stop-top">
                  <span className="stop-kind">{KIND_LABEL[stop.kind] || stop.kind}</span>
                  <span className="stop-time">
                    {formatTime(stop.start)} – {formatTime(stop.end)}
                  </span>
                </div>
                <div className="stop-name">
                  {stop.title} {locked ? <span title="Locked — kept when regenerating">🔒</span> : null}
                </div>
                <div className="stop-address">
                  <span>📍 {v?.address || "address unknown"}</span>
                  {mapsUrl ? (
                    <a href={mapsUrl} target="_blank" rel="noreferrer">
                      Open in Google Maps ↗
                    </a>
                  ) : null}
                </div>
                <div className="stop-body">
                  <div className="stop-reason">{stop.note}</div>
                  <div className="stop-facts">
                    {v?.rating ? (
                      <div className="fact">
                        <span>Rating</span>
                        <span>⭐ {v.rating}</span>
                      </div>
                    ) : null}
                    <div className="fact">
                      <span>Cost</span>
                      <span>
                        {stop.cost_per_person != null ? `$${stop.cost_per_person}/person` : "unknown"}
                        {!stop.cost_verified ? <span className="unverified"> (est.)</span> : null}
                      </span>
                    </div>
                    {stop.travel_from_previous_min != null ? (
                      <div className="fact">
                        <span>From previous</span>
                        <span>
                          {stop.travel_from_previous_min} min{" "}
                          {stop.travel_from_previous_mode === "driving"
                            ? "drive"
                            : stop.travel_from_previous_mode === "transit"
                              ? "transit"
                              : "walk"}
                          {stop.travel_from_previous_source === "estimated" ? (
                            <span className="unverified"> (est.)</span>
                          ) : null}
                        </span>
                      </div>
                    ) : null}
                  </div>
                </div>
                {onSwap ? (
                  <div className="stop-actions">
                    <button type="button" className="mini-btn" onClick={() => onSwap(i)} disabled={busy}>
                      🔁 Swap this stop
                    </button>
                    {onToggleLock ? (
                      <button
                        type="button"
                        className={`mini-btn ${locked ? "on" : ""}`}
                        onClick={() => onToggleLock(i)}
                        disabled={busy}
                      >
                        {locked ? "🔓 Unlock" : "🔒 Lock"}
                      </button>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>

      {itinerary.stops.length > 1 ? (
        <div className="travel-line">Travel times between stops shown on each card</div>
      ) : null}

      <BudgetBox budget={itinerary.budget} />

      {itinerary.edits?.length ? (
        <div className="itin-notes">
          {itinerary.edits.map((n, i) => (
            <div className="itin-note" key={i}>
              ℹ️ {n}
            </div>
          ))}
        </div>
      ) : null}

      {demo ? (
        <p style={{ color: "var(--muted-2)", fontSize: 12.5, marginTop: 14 }}>
          🧪 These are clearly-labeled sample places. Connect a Google Places API key for live venues.
        </p>
      ) : null}
    </section>
  );
}

export function BudgetBox({ budget }) {
  if (!budget) return null;
  const over = budget.remaining < 0;
  return (
    <div className="budget-box">
      <h3>💰 Budget check — per person</h3>
      {budget.lines.map((l, i) => (
        <div className="budget-line" key={i}>
          <span>{l.label}</span>
          <span>
            ${l.amount}
            {!l.verified ? <span className="unverified"> (est.)</span> : null}
          </span>
        </div>
      ))}
      <div className="budget-line total">
        <span>Estimated total</span>
        <span>${budget.per_person_total} of ${budget.budget}</span>
      </div>
      <div className={`budget-line ${over ? "over" : "remaining"}`}>
        <span>{over ? "Over budget" : "Remaining"}</span>
        <span>${Math.abs(budget.remaining)}/person</span>
      </div>
      <div className="budget-note">{budget.note}</div>
    </div>
  );
}
