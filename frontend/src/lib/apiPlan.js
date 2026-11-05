/* Payload adapter: the form works in camelCase (JS-friendly), the API
   contract (backend/app/schemas.py) is snake_case. This is the ONE place
   the conversion happens — form submit, Surprise Me, and edit requests all
   go through it so the two sides can never drift again. */

export function toApiPlan(p) {
  if (!p) return null;
  return {
    city: p.city,
    state: p.state,
    date: p.date,
    group_size: p.groupSize,
    budget: p.budget,
    start_time: p.startTime,
    end_time: p.endTime,
    restrictions: p.restrictions ?? [],
    activities: p.activities ?? [],
    atmosphere: p.atmosphere,
    transport: p.transport,
    distance: p.distance,
    notes: p.notes ?? "",
  };
}
