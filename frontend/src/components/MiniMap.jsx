/* Mini-map: a dependency-free "your night at a glance" scatter of the stops,
   positioned by their real coordinates, plus a one-click full map link.
   The full map opens Google Maps with every stop pre-loaded as a route. */

export function fullMapsUrl(stops) {
  const coords = (stops || [])
    .map((s) => s?.venue)
    .filter((v) => v && v.lat != null && v.lng != null)
    .map((v) => `${v.lat},${v.lng}`);
  if (coords.length === 0) return null;
  return `https://www.google.com/maps/dir/${coords.join("/")}`;
}

export default function MiniMap({ stops }) {
  const points = (stops || [])
    .map((s, i) => ({ i, lat: s?.venue?.lat, lng: s?.venue?.lng, name: s?.title }))
    .filter((p) => p.lat != null && p.lng != null);
  if (points.length < 2) return null;

  const lats = points.map((p) => p.lat);
  const lngs = points.map((p) => p.lng);
  const pad = Math.max((Math.max(...lats) - Math.min(...lats)) * 0.25, 0.001);
  const W = 640;
  const H = 240;
  const spanLat = Math.max(...lats) - Math.min(...lats) + 2 * pad || 0.01;
  const spanLng = Math.max(...lngs) - Math.min(...lngs) + 2 * pad || 0.01;
  const x = (p) => ((p.lng - (Math.min(...lngs) - pad)) / spanLng) * W;
  const y = (p) => H - ((p.lat - (Math.min(...lats) - pad)) / spanLat) * H;

  const line = points.map((p) => `${x(p).toFixed(1)},${y(p).toFixed(1)}`).join(" ");
  const url = fullMapsUrl(stops);

  return (
    <div className="minimap">
      <div className="minimap-head">
        <span>🗺️ Your night at a glance</span>
        {url ? (
          <a href={url} target="_blank" rel="noreferrer">
            View full map with all stops ↗
          </a>
        ) : null}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Map of your stops">
        <defs>
          <linearGradient id="mm-line" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>
        {/* faint dot grid for a map-like feel */}
        {Array.from({ length: 9 }).map((_, r) =>
          Array.from({ length: 14 }).map((_, c) => (
            <circle key={`${r}-${c}`} cx={20 + c * 46} cy={16 + r * 26} r="1.1" fill="rgba(255,255,255,0.07)" />
          ))
        )}
        <polyline points={line} fill="none" stroke="url(#mm-line)" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" strokeDasharray="1 0" opacity="0.85" />
        {points.map((p) => (
          <g key={p.i}>
            <circle cx={x(p)} cy={y(p)} r="13" fill="rgba(11,16,32,0.9)" stroke="#8b5cf6" strokeWidth="1.5" />
            <circle cx={x(p)} cy={y(p)} r="6.5" fill="url(#mm-line)" />
            <text x={x(p)} y={y(p) + 3.5} textAnchor="middle" fontSize="8.5" fontWeight="700" fill="#fff">
              {p.i + 1}
            </text>
            <text x={x(p)} y={y(p) - 18} textAnchor="middle" fontSize="11" fill="rgba(255,255,255,0.75)" fontWeight="600">
              {p.name.length > 22 ? p.name.slice(0, 21) + "…" : p.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
