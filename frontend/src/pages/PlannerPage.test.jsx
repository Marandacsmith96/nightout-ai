// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { JSDOM } from "jsdom";
import PlannerPage from "./PlannerPage.jsx";
import { api } from "../api/client.js";
import { toApiPlan } from "../lib/apiPlan.js";
import { encodeShare } from "../lib/share.js";
import { toLocalDateStr } from "../lib/nightOptions.js";

vi.mock("../api/client.js", () => ({ api: { generateNight: vi.fn(), editNight: vi.fn() } }));

const plan = { city: "Denver", state: "CO", date: "2026-12-05", groupSize: 4, budget: 60,
  startTime: "18:00", endTime: "23:30", activities: ["Dinner"], restrictions: [], transport: "Walking" };
function itinerary(p = plan) {
  return { id: "test", city: p.city, date: p.date, request: toApiPlan(p), demo: true, edits: [],
    stops: ["dinner", "games & arcade bars"].map((kind, i) => ({ index: i + 1, kind, title: `Venue ${i}`,
      venue: { id: `v${i}`, address: "Denver", lat: 39.7, lng: -105 }, start: p.startTime, end: "21:00", cost_per_person: 10 })),
    budget: { lines: [], per_person_total: 20, budget: p.budget, remaining: p.budget - 20 } };
}
function restore(p = plan) {
  window.history.replaceState(null, "", `/#${encodeShare({ plan: p, itinerary: itinerary(p) })}`);
  return render(<PlannerPage />);
}

beforeEach(() => {
  vi.clearAllMocks();
  // Node 26 exposes its own storage global; use an actual DOM Storage instance.
  vi.stubGlobal("localStorage", new JSDOM("", { url: "http://localhost" }).window.localStorage);
  localStorage.clear();
  window.history.replaceState(null, "", "/");
  Element.prototype.scrollIntoView = vi.fn();
  api.generateNight.mockImplementation(async (p) => itinerary(p));
  api.editNight.mockImplementation(async ({ request }) => ({ itinerary: itinerary(request), reply: "Updated" }));
});
afterEach(cleanup);

describe("itinerary preferences", () => {
  it("uses Surprise Me preferences for edits and saved nights from a blank form", async () => {
    render(<PlannerPage />);
    fireEvent.click(screen.getByRole("button", { name: /pick everything for us/i }));
    await screen.findByRole("button", { name: /regenerate/i });
    const generated = api.generateNight.mock.calls[0][0];
    fireEvent.click(screen.getByRole("button", { name: /regenerate/i }));
    await waitFor(() => expect(api.editNight).toHaveBeenCalled());
    expect(api.editNight.mock.calls[0][0].request).toMatchObject(generated);
    await waitFor(() => expect(screen.getByRole("button", { name: /regenerate/i }).disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: /^💾 Save$/ }));
    expect(JSON.parse(localStorage.getItem("nightout-saved"))[0].plan).toMatchObject(generated);
  });

  it("keeps chat changes for later edits even when the form draft changes", async () => {
    restore();
    await screen.findByRole("button", { name: /regenerate/i });
    api.editNight.mockResolvedValueOnce({ itinerary: itinerary({ ...plan, startTime: "19:00", budget: 40 }), reply: "Changed start" });
    fireEvent.click(screen.getByRole("button", { name: /finish by 10 PM/i }));
    await screen.findByText("Changed start");
    fireEvent.change(screen.getByPlaceholderText("e.g. Denver"), { target: { value: "Austin" } });
    fireEvent.click(screen.getAllByRole("button", { name: /swap this stop/i })[0]);
    await waitFor(() => expect(api.editNight).toHaveBeenCalledTimes(2));
    expect(api.editNight.mock.calls[1][0].request).toMatchObject({ city: "Denver", startTime: "19:00", budget: 40 });
  });

  it("keeps locks attached to venue identity after stops move", async () => {
    restore();
    await screen.findByRole("button", { name: /regenerate/i });
    fireEvent.click(screen.getAllByRole("button", { name: /^🔒 Lock$/ })[1]);
    const moved = itinerary();
    moved.stops = [...moved.stops].reverse().map((s, i) => ({ ...s, index: i + 1 }));
    api.editNight.mockResolvedValueOnce({ itinerary: moved, reply: "Moved" });
    fireEvent.click(screen.getByRole("button", { name: /regenerate/i }));
    await waitFor(() => expect(screen.getByRole("button", { name: /regenerate/i }).disabled).toBe(false));
    await waitFor(() => expect(screen.getAllByRole("button", { name: /swap this stop/i })[0].disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: /regenerate/i }));
    await waitFor(() => expect(api.editNight).toHaveBeenCalledTimes(2));
    expect(api.editNight.mock.calls[0][0].lockedIndices).toEqual([1]);
    expect(api.editNight.mock.calls[1][0].lockedIndices).toEqual([0]);
  });

  it("accepts today locally and preserves custom dietary text through generation and editing", async () => {
    const { container } = render(<PlannerPage />);
    fireEvent.change(screen.getByPlaceholderText("e.g. Denver"), { target: { value: "Denver" } });
    fireEvent.change(container.querySelector('input[type="date"]'), { target: { value: toLocalDateStr(new Date()) } });
    fireEvent.click(screen.getByRole("button", { name: "Other (type below)" }));
    fireEvent.change(screen.getByPlaceholderText("e.g. nut allergy"), { target: { value: "No sesame" } });
    fireEvent.click(screen.getByRole("button", { name: /Generate My Night Out/i }));
    await screen.findByRole("button", { name: /regenerate/i });
    expect(api.generateNight.mock.calls[0][0].restrictions).toEqual(["No sesame"]);
    fireEvent.click(screen.getByRole("button", { name: /regenerate/i }));
    await waitFor(() => expect(api.editNight).toHaveBeenCalled());
    expect(api.editNight.mock.calls[0][0].request.restrictions).toEqual(["No sesame"]);
  });
});
