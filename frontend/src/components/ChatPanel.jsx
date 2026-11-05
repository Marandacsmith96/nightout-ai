import { useState } from "react";
import "../chat.css";

const SUGGESTIONS = [
  "Make dinner cheaper",
  "Swap the bar for dessert",
  "We want to finish by 10 PM",
  "Make the night more adventurous",
  "Add a live music stop",
  "Two more vegetarians joined",
];

export default function ChatPanel({ onSend, busy }) {
  const [messages, setMessages] = useState([{ role: "ai", text: "Hey! Want to tweak the night? Try \u201CMake dinner cheaper\u201D or \u201Cwe finish by 10 PM now\u201D." }]);
  const [draft, setDraft] = useState("");

  async function send(text) {
    const trimmed = (text ?? draft).trim();
    if (!trimmed || busy) return;
    setDraft("");
    setMessages((m) => [...m, { role: "user", text: trimmed }]);
    try {
      const reply = await onSend(trimmed);
      setMessages((m) => [...m, { role: "ai", text: reply }]);
    } catch {
      setMessages((m) => [...m, { role: "ai", text: "Hmm, I couldn't reach the planner. Is the backend running?" }]);
    }
  }

  return (
    <div className="chat">
      <div className="chat-head">💬 Tweak your night with AI</div>
      <div className="chat-body">
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role === "user" ? "user" : "ai"}`}>
            {m.text}
          </div>
        ))}
        {busy ? (
          <div className="chat-msg ai">
            <span className="chat-typing">Thinking</span>
            <span className="typing-dots"><i /><i /><i /></span>
          </div>
        ) : null}
      </div>
      <div className="chat-suggestions">
        {SUGGESTIONS.map((s) => (
          <button key={s} type="button" className="chat-suggestion" onClick={() => send(s)} disabled={busy}>
            {s}
          </button>
        ))}
      </div>
      <form
        className="chat-form"
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
      >
        <input
          className="chat-input"
          placeholder="Tell the AI what to change…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          disabled={busy}
          aria-label="Edit instruction"
        />
        <button type="submit" className="btn btn-primary" disabled={busy || !draft.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
