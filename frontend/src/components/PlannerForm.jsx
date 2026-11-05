import { useEffect, useMemo, useState } from "react";
import { Button, Chip, Field, Stepper, BudgetSlider } from "./kit.jsx";
import {
  ACTIVITIES, ATMOSPHERES, BUDGET_PRESETS, DISTANCE_PREFS,
  FOOD_RESTRICTIONS, TRANSPORT, formatTime,
} from "../lib/nightOptions.js";

const EMPTY = {
  city: "", state: "", date: "", groupSize: 4,
  budget: 60, startTime: "19:00", endTime: "23:30",
  restrictions: [], otherRestriction: "", activities: ["Dinner"],
  atmosphere: "Casual & relaxed", transport: "Walking",
  distance: "Moderate travel between stops is okay", notes: "",
};

export default function PlannerForm({ onPlanChange, onGenerate }) {
  const [p, setP] = useState(EMPTY);
  const [errors, setErrors] = useState({});

  useEffect(() => { onPlanChange(p); }, [p]); // eslint-disable-line react-hooks/exhaustive-deps

  const set = (patch) => setP((prev) => ({ ...prev, ...patch }));

  const toggleMulti = (key, value) =>
    setP((prev) => ({
      ...prev,
      [key]: prev[key].includes(value) ? prev[key].filter((v) => v !== value) : [...prev[key], value],
    }));

  // "Other" food restriction: selecting it reveals a text box that holds the value.
  const restrictionValues = useMemo(
    () => p.restrictions.filter((r) => r !== "Other (type below)"),
    [p.restrictions]
  );
  const otherActive = p.restrictions.includes("Other (type below)");

  function validate() {
    const e = {};
    if (!p.city.trim()) e.city = "Enter a city (e.g. Denver).";
    if (!p.date) e.date = "Pick the date of your night out.";
    if (p.date && new Date(p.date) < new Date(new Date().toDateString())) e.date = "That date is in the past.";
    if (!p.startTime) e.startTime = "Pick a start time.";
    if (!p.endTime) e.endTime = "Pick an end time.";
    if (p.startTime && p.endTime && p.endTime <= p.startTime && p.endTime > "03:00")
      e.endTime = "End time is before the start — if the night ends after midnight, use a time up to 3:00 AM.";
    if (p.activities.length === 0) e.activities = "Pick at least one activity.";
    if (otherActive && !p.otherRestriction.trim()) e.otherRestriction = "Type your restriction, or uncheck \u201COther\u201D.";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  function submit(ev) {
    ev.preventDefault();
    if (!validate()) return;
    const { otherRestriction, ...rest } = p;
    const restrictions = [...restrictionValues, ...(otherActive ? [otherRestriction.trim()] : [])];
    onGenerate({ ...rest, restrictions });
  }

  const today = new Date().toISOString().split("T")[0];

  return (
    <form noValidate onSubmit={submit}>
      <div className="form-grid">
        <Field label="City" error={errors.city}>
          <input className={`input${errors.city ? " invalid" : ""}`} placeholder="e.g. Denver" value={p.city}
            onChange={(e) => set({ city: e.target.value })} />
        </Field>
        <Field label="State / region" hint="optional">
          <input className="input" placeholder="e.g. CO" value={p.state} onChange={(e) => set({ state: e.target.value })} />
        </Field>

        <Field label="Date" error={errors.date}>
          <input type="date" min={today} className={`input${errors.date ? " invalid" : ""}`} value={p.date}
            onChange={(e) => set({ date: e.target.value })} />
        </Field>
        <Field label="Group size" hint="1–20 people">
          <Stepper value={p.groupSize} onChange={(v) => set({ groupSize: v })} label="Group size" />
        </Field>

        <Field label="Budget" full>
          <div className="budget-preset">
            {BUDGET_PRESETS.map((b) => (
              <Chip key={b.value} single label={b.label} active={p.budget === b.value}
                onClick={() => set({ budget: b.value })} />
            ))}
          </div>
          <div className="budget-row">
            <BudgetSlider value={p.budget} onChange={(v) => set({ budget: v })} />
            <Field label="Or exact amount" hint="$ per person">
              <input type="number" min={5} max={1000} className="input" style={{ width: 130 }} value={p.budget}
                onChange={(e) => set({ budget: Math.max(5, Number(e.target.value) || 5) })} />
            </Field>
          </div>
        </Field>

        <Field label="Start time" hint="when the night kicks off" error={errors.startTime}>
          <input type="time" className={`input${errors.startTime ? " invalid" : ""}`} value={p.startTime}
            onChange={(e) => set({ startTime: e.target.value })} />
        </Field>
        <Field label="End time" hint="nights ending after midnight are fine" error={errors.endTime}>
          <input type="time" className={`input${errors.endTime ? " invalid" : ""}`} value={p.endTime}
            onChange={(e) => set({ endTime: e.target.value })} />
        </Field>

        <Field label="Food preferences & restrictions" hint="choose any, plus optional 'Other'" full
          error={errors.restrictions}>
          <div className="chips">
            {FOOD_RESTRICTIONS.map((r) => (
              <Chip key={r} label={r} active={p.restrictions.includes(r)}
                onClick={() => toggleMulti("restrictions", r)} />
            ))}
          </div>
          {otherActive && (
            <Field label="Other restriction" error={errors.otherRestriction}>
              <input className="input" placeholder="e.g. nut allergy" value={p.otherRestriction}
                onChange={(e) => set({ otherRestriction: e.target.value })} />
            </Field>
          )}
        </Field>

        <Field label="Preferred activities" hint="pick any mix" full error={errors.activities}>
          <div className="chips">
            {ACTIVITIES.map((a) => (
              <Chip key={a} label={a} active={p.activities.includes(a)} onClick={() => toggleMulti("activities", a)} />
            ))}
          </div>
        </Field>

        <Field label="Preferred atmosphere" full>
          <div className="chips">
            {ATMOSPHERES.map((a) => (
              <Chip key={a} single label={a} active={p.atmosphere === a} onClick={() => set({ atmosphere: a })} />
            ))}
          </div>
        </Field>

        <Field label="Getting around" full>
          <div className="chips">
            {TRANSPORT.map((t) => (
              <Chip key={t} single label={t} active={p.transport === t} onClick={() => set({ transport: t })} />
            ))}
          </div>
        </Field>

        <Field label="Travel distance preference" full>
          <div className="chips">
            {DISTANCE_PREFS.map((d) => (
              <Chip key={d} single label={d} active={p.distance === d} onClick={() => set({ distance: d })} />
            ))}
          </div>
        </Field>

        <Field label="Anything else?" hint="natural language welcome" full>
          <textarea className="textarea" placeholder={'e.g. "Six of us, casual Friday night in Denver, one vegetarian, dinner and a fun activity, no clubs, under $60 each, keep it close together."'}
            value={p.notes} onChange={(e) => set({ notes: e.target.value })} />
        </Field>
      </div>

      <div style={{ marginTop: 26 }}>
        <Button type="submit" size="lg" className="btn-block">✨ Generate My Night Out</Button>
        <p style={{ textAlign: "center", color: "var(--muted-2)", fontSize: 12.5, marginTop: 12 }}>
          Plan starts {p.startTime ? formatTime(p.startTime) : "—"} · ends {p.endTime ? formatTime(p.endTime) : "—"} ·
          budget ${p.budget}/person
        </p>
      </div>
    </form>
  );
}
