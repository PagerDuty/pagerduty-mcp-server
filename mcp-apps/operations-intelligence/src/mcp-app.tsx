/**
 * Operations Intelligence v2 - Main App
 *
 * Two tabs:
 *   Operational: KPI bar + Service / Team / Responder metric tables
 *   Insights:    Auto-generated AI summary cards + follow-up chat
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchOpsData, type OpsData } from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { SummaryCards } from "./components/SummaryCards";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { TeamBreakdown } from "./components/TeamBreakdown";
import { ResponderLoad } from "./components/ResponderLoad";
import { InsightsTab } from "./components/InsightsTab";

type Tab = "operational" | "insights";

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
    appInfo: { name: "Operations Intelligence", version: "2.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [tab, setTab] = useState<Tab>("operational");
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [selectedTeam, setSelectedTeam] = useState<string>("");
  // refreshKey increments on each Refresh click to trigger InsightsTab re-fetch
  const [refreshKey, setRefreshKey] = useState(0);

  const [data, setData] = useState<OpsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    setRefreshKey((k) => k + 1);
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

  const selectedTeamName = useMemo(() => {
    if (!selectedTeam || !data) return "";
    return data.teams.find((t) => t.id === selectedTeam)?.name ?? "";
  }, [selectedTeam, data]);

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

      <div className="tabs">
        <button
          className={`tab-btn${tab === "operational" ? " tab-active" : ""}`}
          onClick={() => setTab("operational")}
        >
          Operational
        </button>
        <button
          className={`tab-btn${tab === "insights" ? " tab-active" : ""}`}
          onClick={() => setTab("insights")}
        >
          Insights
        </button>
      </div>

      {displayError && <div className="error-state">{displayError}</div>}

      {loading && !data ? (
        <div className="loading">Loading operational data…</div>
      ) : tab === "operational" && data ? (
        <div className="body">
          <SummaryCards data={data} />
          <ServiceBreakdown metrics={data.serviceMetrics} />
          <TeamBreakdown metrics={data.teamMetrics} />
          <ResponderLoad metrics={data.responderMetrics} />
        </div>
      ) : tab === "insights" && app ? (
        <InsightsTab
          app={app}
          teamName={selectedTeamName}
          since={since}
          until={until}
          refreshKey={refreshKey}
        />
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
