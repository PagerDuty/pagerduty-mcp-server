import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { triggerSreAgent } from "../api";

interface SreAgentModalProps {
  app: App;
  incidentId: string;
  incidentNumber: number;
  onClose: () => void;
}

export function SreAgentModal({ app, incidentId, incidentNumber, onClose }: SreAgentModalProps) {
  const [loading, setLoading] = useState(true);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    triggerSreAgent(app, incidentId).then((result) => {
      if (cancelled) return;
      setLoading(false);
      if (result.success) {
        setSent(true);
      } else {
        setError(result.error ?? "Failed to trigger SRE Agent.");
      }
    });

    return () => { cancelled = true; };
  }, [app, incidentId]);

  return (
    <div className="sre-agent-overlay" onClick={(e) => e.stopPropagation()}>
      <div className="sre-agent-modal">
        <div className="sre-agent-header">
          <span>✨ SRE Agent — Incident #{incidentNumber}</span>
          <button className="sre-agent-close" onClick={onClose} aria-label="Close">✕</button>
        </div>
        <div className="sre-agent-body">
          {loading && (
            <div className="sre-agent-loading">
              <div className="spinner" />
              <p>Triggering SRE Agent...</p>
            </div>
          )}
          {!loading && sent && (
            <div className="sre-agent-sent">
              <p>✅ SRE Agent triggered for incident #{incidentNumber}.</p>
              <p className="sre-agent-hint">The analysis is running in the chat thread above.</p>
              <button className="btn-primary" onClick={onClose}>Close</button>
            </div>
          )}
          {!loading && error && (
            <div className="sre-agent-error">
              <p>⚠️ {error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
