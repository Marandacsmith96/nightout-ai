import { useEffect, useRef, useState } from "react";
import PlannerForm from "../components/PlannerForm.jsx";
import ItineraryView from "../components/ItineraryView.jsx";
import ChatPanel from "../components/ChatPanel.jsx";
import MediaModal from "../components/MediaModal.jsx";
import { LoadingOverlay } from "../components/kit.jsx";
import { api } from "../api/client.js";
import { localMidnight, summarizeNight } from "../lib/nightOptions.js";
import {
  copyText, decodeShare, deleteSaved, encodeShare, itineraryText,
  loadSaved, saveNight,
} from "../lib/share.js";

export default function PlannerPage() {
  const [plan, setPlan] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [editing, setEditing] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [error, setError] = useState(null);
  const [locked, setLocked] = useState([]); // stop indices
  const [savedList, setSavedList] = useState(loadSaved());
  const [flash, setFlash] = useState(null); // small toast-ish message
  const [media, setMedia] = useState(null); // Phase 7: open media modal (poster / voice-over)
  const [mediaBusy, setMediaBusy] = useState(null); // "poster" | "voiceover" | null
  const resultsRef = useRef(null);

  // Restore a shared itinerary from the URL fragment (#...), e.g. after a friend
  // opens a share link on this machine's browser.
  useEffect(() => {
    const hash = window.location.hash.replace(/^#/, "");
    if (!hash) return;
    const shared = decodeShare(hash);
    if (shared?.itinerary) {
      setPlan(shared.plan || null);
      setItinerary(shared.itinerary);
      setLocked([]);
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth" }), 120);
    }
  }, []);

  function scrollToResults() {
    setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
  }

  async function handleGenerate(payload) {
    setGenerating(true);
    setError(null);
    setLocked([]);
    try {
      const result = await api.generateNight(payload);
      setItinerary(result);
      scrollToResults();
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setGenerating(false);
    }
  }

  /** Send a conversational edit; returns the assistant's reply text. */
  async function handleEdit(instruction) {
    if (!plan || !itinerary) return "";
    setEditing(true);
    try {
      const res = await api.editNight({
        instruction,
        request: plan,
        itinerary,
        lockedIndices: locked,
      });
      setItinerary(res.itinerary);
      return res.reply || "Done!";
    } catch (err) {
      return `That change didn't go through (${err.message}). Try a different wording?`;
    } finally {
      setEditing(false);
    }
  }

  function handleSwap(index) {
    const stop = itinerary?.stops[index];
    const kind = stop ? stop.kind : "this stop";
    return handleEdit(`Swap stop ${index + 1} (${kind}) for a different venue`);
  }

  function handleRegenerate() {
    return handleEdit("Replan the entire night from scratch, keeping the same preferences");
  }

  function toggleLock(index) {
    setLocked((prev) => (prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]));
  }

  function handleSave() {
    const list = saveNight({ plan, itinerary });
    setSavedList(list);
    setFlash("Saved to your nights 💾");
  }

  function handleCopy() {
    copyText(itineraryText(itinerary)).then((ok) =>
      setFlash(ok ? "Copied — paste it in the group chat 📋" : "Couldn't copy — select/tap the text manually.")
    );
  }

  function handleShareLink() {
    const url = `${window.location.origin}${window.location.pathname}#${encodeShare({ plan, itinerary })}`;
    copyText(url).then((ok) =>
      setFlash(ok ? "Share link copied — anyone with this link can open it 🔗" : "Couldn't copy the link.")
    );
  }

  // Phase 7: multimodal media — promo poster (FLUX) + voice-over (Chatterbox).
  function mediaDateLabel() {
    return localMidnight(itinerary.date).toLocaleDateString(undefined, {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  }

  async function handlePoster() {
    if (!itinerary) return;
    setMediaBusy("poster");
    try {
      const res = await api.poster(itinerary);
      if (!res.available) {
        setFlash(res.note || "Poster studio isn't available right now.");
        return;
      }
      setMedia({
        type: "poster",
        dataUrl: `data:${res.media_type};base64,${res.data_b64}`,
        sourceLabel: res.source_label,
        prompt: res.prompt,
        city: itinerary.city,
        dateLabel: mediaDateLabel(),
      });
    } catch (err) {
      setFlash(err.message || "Poster generation failed.");
    } finally {
      setMediaBusy(null);
    }
  }

  async function handleVoiceover() {
    if (!itinerary) return;
    setMediaBusy("voiceover");
    try {
      const res = await api.voiceover(itinerary);
      if (!res.available) {
        setFlash(res.note || "Voice-over isn't available right now.");
        return;
      }
      setMedia({
        type: "voiceover",
        dataUrl: `data:${res.media_type};base64,${res.data_b64}`,
        mediaType: res.media_type,
        sourceLabel: res.source_label,
        narration: res.narration,
        city: itinerary.city,
        dateLabel: mediaDateLabel(),
      });
    } catch (err) {
      setFlash(err.message || "Voice-over generation failed.");
    } finally {
      setMediaBusy(null);
    }
  }

  function loadSavedNight(item) {
    setPlan(item.plan || null);
    setItinerary(item.itinerary);
    setLocked([]);
    setFlash(`Loaded “${item.label}”`);
    scrollToResults();
  }

  const currentSaved = itinerary ? savedList.some((s) => s.itinerary?.id === itinerary.id) : false;

  return (
    <div className="container" style={{ paddingTop: 44, paddingBottom: 30 }}>
      <h1 style={{ fontSize: "clamp(28px, 4.5vw, 40px)", fontWeight: 800, marginBottom: 6 }}>
        Plan <span className="gradient">My Night</span>
      </h1>
      <p style={{ color: "var(--muted)", maxWidth: 640, margin: "0 0 30px" }}>
        A minute of details now saves an hour of group-chat chaos later.
      </p>

      <div className="planner-grid">
        <section className="panel">
          <h2>Your night, your way</h2>
          <p className="panel-sub">Everything below can be changed later by chatting with the AI.</p>
          <PlannerForm onPlanChange={setPlan} onGenerate={handleGenerate} />
        </section>

        <aside className="panel live-summary">
          <h3>Your night so far</h3>
          {summarizeNight(plan).map(([k, v]) => (
            <div className="live-row" key={k}>
              <span>{k}</span>
              <span>{v}</span>
            </div>
          ))}
          {plan?.notes ? (
            <div style={{ marginTop: 12, fontSize: 12.5, color: "var(--muted-2)" }}>
              “{plan.notes.length > 140 ? plan.notes.slice(0, 140) + "…" : plan.notes}”
            </div>
          ) : null}

          {savedList.length > 0 ? (
            <div className="saved-nights">
              <h4>💾 My saved nights</h4>
              {savedList.map((s) => (
                <div className="saved-row" key={s.itinerary.id}>
                  <button type="button" className="saved-open" onClick={() => loadSavedNight(s)}>
                    {s.label} · {s.itinerary.stops.length} stops
                  </button>
                  <button
                    type="button"
                    className="saved-del"
                    title="Delete"
                    onClick={() => setSavedList(deleteSaved(s.itinerary.id))}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          ) : null}
        </aside>
      </div>

      {error ? (
        <section ref={resultsRef} style={{ marginTop: 34 }} className="panel">
          <h2 style={{ marginBottom: 10 }}>Something went wrong</h2>
          <div className="error-box">{error}</div>
          <p style={{ color: "var(--muted)", fontSize: 13.5, margin: 0 }}>
            Check that the backend is running (<code>uvicorn app.main:app --port 8000</code> in{" "}
            <code>backend/</code>) and try again — or adjust your search (another city, a higher budget,
            or different activities).
          </p>
        </section>
      ) : null}

      {itinerary ? (
        <section ref={resultsRef} style={{ marginTop: 34 }} className="panel">
          <ItineraryView
            itinerary={itinerary}
            onRegenerate={handleRegenerate}
            busy={generating || editing}
            onSwap={handleSwap}
            lockedIndices={locked}
            onToggleLock={toggleLock}
            onSave={handleSave}
            saved={currentSaved}
            onCopy={handleCopy}
            onShareLink={handleShareLink}
            onPoster={handlePoster}
            onVoiceover={handleVoiceover}
            mediaBusy={mediaBusy}
          />
          <ChatPanel onSend={handleEdit} busy={editing || generating} />
        </section>
      ) : null}

      {flash ? <div className="flash-note">✨ {flash}</div> : null}

      {media ? <MediaModal media={media} onClose={() => setMedia(null)} /> : null}

      {generating && !itinerary ? (
        <LoadingOverlay title="Planning your perfect night…" sub="Picking real places that fit your group, budget, and time — this only takes a few seconds." />
      ) : null}
    </div>
  );
}
