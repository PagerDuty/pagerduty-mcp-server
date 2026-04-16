/**
 * Operations Intelligence - Main App
 *
 * Controls bar: team picker + date range + refresh
 * Summary cards: total incidents, high urgency, avg MTTR, on-call users
 * Service breakdown: bar chart table
 * Incident table: sortable list
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchOpsData, type OpsData, type RecentIncident } from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { SummaryCards } from "./components/SummaryCards";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { IncidentTable, type SortKey } from "./components/IncidentTable";

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

function sortIncidents(incidents: RecentIncident[], key: SortKey, dir: "asc" | "desc"): RecentIncident[] {
  return [...incidents].sort((a, b) => {
    let av: string | number = a[key] ?? "";
    let bv: string | number = b[key] ?? "";
    if (key === "mttrMinutes") {
      av = a.mttrMinutes ?? Infinity;
      bv = b.mttrMinutes ?? Infinity;
    }
    if (av < bv) return dir === "asc" ? -1 : 1;
    if (av > bv) return dir === "asc" ? 1 : -1;
    return 0;
  });
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Operations Intelligence", version: "1.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [selectedTeam, setSelectedTeam] = useState<string>("");

  const [data, setData] = useState<OpsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sortKey, setSortKey] = useState<SortKey>("createdAt");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const load = useCallback(async () => {
    if (!app) return;
    setLoading(true);
    setError(null);
    try {
      const d = await fetchOpsData(
        app,
        new Date(since).toISOString(),
        new Date(until + "T23:59:59").toISOString(),
        selectedTeam || null
      );
      setData(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [app, since, until, selectedTeam]);

  useEffect(() => {
    load();
  }, [load]);

  function handleSort(key: SortKey) {
    if (key === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("desc"); }
  }

  const sortedIncidents = useMemo(
    () => sortIncidents(data?.recentIncidents ?? [], sortKey, sortDir),
    [data, sortKey, sortDir]
  );

  const maxServiceCount = useMemo(
    () => Math.max(1, ...(data?.serviceStats ?? []).map((s) => s.incidentCount)),
    [data]
  );

  const displayError = connectionError?.message ?? error;

  return (
    <div className="app">
      <header className="app-header">
        <span className="pd-icon"><PagerDutyLogo size={22} /></span>
        <h1>Operations Intelligence</h1>
      </header>

      <div className="controls">
        <label>Team</label>
        <select value={selectedTeam} onChange={(e) => setSelectedTeam(e.currentTarget.value)}>
          <option value="">All teams</option>
          {(data?.teams ?? []).map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <label>From</label>
        <input type="date" value={since} onChange={(e) => setSince(e.currentTarget.value)} />
        <label>To</label>
        <input type="date" value={until} onChange={(e) => setUntil(e.currentTarget.value)} />
        <button className="btn btn-primary btn-sm" onClick={load} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </button>
      </div>

      {displayError && <div className="error-state">{displayError}</div>}

      {loading && !data ? (
        <div className="loading">Loading operational data…</div>
      ) : data ? (
        <div className="body">
          <SummaryCards data={data} />
          <ServiceBreakdown stats={data.serviceStats.slice(0, 10)} max={maxServiceCount} />
          <IncidentTable
            incidents={sortedIncidents}
            sortKey={sortKey}
            sortDir={sortDir}
            onSort={handleSort}
          />
        </div>
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
