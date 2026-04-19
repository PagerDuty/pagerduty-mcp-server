import { useEffect, useRef, useState } from "react";
import type { InsightMessage } from "../api";

interface InsightsChatProps {
  messages: InsightMessage[];
  loading: boolean;
  onSend: (message: string) => void;
}

export function InsightsChat({ messages, loading, onSend }: InsightsChatProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  function handleSend() {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput("");
    onSend(msg);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel-title">Ask a follow-up question</div>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state" style={{ padding: "20px 0" }}>
            Ask anything about your operational metrics, trends, or team performance.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-message ${m.role === "user" ? "chat-user" : "chat-assistant"}`}>
            <div className="chat-message-role">{m.role === "user" ? "You" : "Insights Agent"}</div>
            <div className="chat-message-content">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="chat-message chat-assistant">
            <div className="chat-message-role">Insights Agent</div>
            <div className="insight-skeleton" style={{ width: "60%", marginTop: 4 }} />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-row">
        <textarea
          className="chat-input"
          placeholder="e.g. Which team had the most sleep interruptions last month?"
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={loading}
        />
        <button
          className="btn btn-primary btn-sm"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
