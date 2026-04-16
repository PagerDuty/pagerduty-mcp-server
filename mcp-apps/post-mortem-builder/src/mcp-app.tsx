/**
 * Post-Mortem Builder - Main App
 *
 * View A — Incident Picker: list resolved incidents, search/filter
 * View B — Timeline View: color-coded event timeline + copy as markdown
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import {
  fetchResolvedIncidents,
  fetchIncidentTimeline,
  exportToMarkdown,
  type IncidentSummary,
  type IncidentTimeline,
} from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { IncidentPicker } from "./components/IncidentPicker";
import { TimelineView } from "./components/TimelineView";

function getDefaultSince(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0]!;
}

function getToday(): string {
  return new Date().toISOString().split("T")[0]!;
}

function detectTheme(): "dark" | "light" {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Post-Mortem Builder", version: "1.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);

  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [search, setSearch] = useState("");
  const [urgencyFilter, setUrgencyFilter] = useState("");
  const [timeline, setTimeline] = useState<IncidentTimeline | null>(null);

  const [loading, setLoading] = useState(false);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Load incidents when app is ready or date range changes
  useEffect(() => {
    if (!app) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchResolvedIncidents(app, new Date(since).toISOString(), new Date(until + "T23:59:59").toISOString())
      .then((data) => { if (!cancelled) setIncidents(data); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load incidents"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [app, since, until]);

  const handleSelectIncident = useCallback(async (id: string) => {
    if (!app) return;
    setTimelineLoading(true);
    setError(null);
    try {
      const t = await fetchIncidentTimeline(app, id);
      setTimeline(t);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load timeline");
    } finally {
      setTimelineLoading(false);
    }
  }, [app]);

  const handleCopyMarkdown = useCallback(() => {
    if (!timeline) return;
    const md = exportToMarkdown(timeline);
    navigator.clipboard.writeText(md).then(() => {
      setToast("Copied to clipboard!");
      setTimeout(() => setToast(null), 2500);
    });
  }, [timeline]);

  const displayError = connectionError?.message ?? error;

  return (
    <div className="app">
      <header className="app-header">
        <span className="pd-icon"><PagerDutyLogo size={22} /></span>
        <h1>Post-Mortem Builder</h1>
      </header>

      {!timeline && (
        <div className="date-controls">
          <label>From</label>
          <input type="date" value={since} onChange={(e) => setSince(e.currentTarget.value)} />
          <label>To</label>
          <input type="date" value={until} onChange={(e) => setUntil(e.currentTarget.value)} />
          <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
            {incidents.length} resolved incident{incidents.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}

      {displayError && <div className="error-state">{displayError}</div>}

      {timelineLoading ? (
        <div className="loading">Loading timeline…</div>
      ) : timeline ? (
        <TimelineView
          timeline={timeline}
          onCopyMarkdown={handleCopyMarkdown}
          onBack={() => setTimeline(null)}
        />
      ) : loading ? (
        <div className="loading">Loading incidents…</div>
      ) : (
        <IncidentPicker
          incidents={incidents}
          onSelect={handleSelectIncident}
          search={search}
          onSearchChange={setSearch}
          urgencyFilter={urgencyFilter}
          onUrgencyChange={setUrgencyFilter}
        />
      )}

      {toast && <div className="success-toast">{toast}</div>}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
