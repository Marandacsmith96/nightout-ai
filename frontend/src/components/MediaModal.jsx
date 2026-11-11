import "../media.css";

/**
 * Modal for Phase 7 AI media: a FLUX promo poster (with caption overlay +
 * the exact prompt shown, honesty-first) or a Chatterbox voice-over.
 * Rendered by PlannerPage; media carries {type, dataUrl, sourceLabel, ...}.
 */
export default function MediaModal({ media, onClose }) {
  if (!media) return null;
  const poster = media.type === "poster";
  return (
    <div
      className="media-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={poster ? "Promo poster for your night out" : "Voice-over for your night out"}
    >
      <div className="media-card" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="media-close" onClick={onClose} aria-label="Close">
          ✕
        </button>

        {poster ? (
          <>
            <div className="poster-frame">
              <img src={media.dataUrl} alt={`AI-generated poster for your ${media.city} night out`} />
              <div className="poster-caption">
                <strong>Your {media.city} Night Out</strong>
                <span>{media.dateLabel}</span>
              </div>
            </div>
            <p className="media-note">✨ {media.sourceLabel} — the exact prompt used:</p>
            <p className="media-prompt">“{media.prompt}”</p>
            <a className="btn btn-primary media-download" href={media.dataUrl} download="nightout-poster.png">
              ⬇️ Download poster
            </a>
          </>
        ) : (
          <>
            <h3 className="media-title">🔊 Hear your night out</h3>
            <audio controls autoPlay src={media.dataUrl} />
            <p className="media-note">✨ {media.sourceLabel} — the exact narration:</p>
            <p className="media-prompt">“{media.narration}”</p>
            <a className="btn btn-primary media-download" href={media.dataUrl} download="nightout-voiceover.mp3">
              ⬇️ Download voice-over
            </a>
          </>
        )}

        <p className="media-disclaimer">
          ✨ {media.sourceLabel} — generated on demand from your itinerary, not real promotional art
        </p>
      </div>
    </div>
  );
}
