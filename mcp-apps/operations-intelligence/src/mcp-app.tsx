import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchOpsData, type OpsData } from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { SummaryCards } from "./components/SummaryCards";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { TeamBreakdown } from "./components/TeamBreakdown";
import { ResponderLoad } from "./components/ResponderLoad";
import { TrendsTab } from "./components/TrendsTab";
import { TeamHealth } from "./components/TeamHealth";
import { PercentileSection } from "./components/PercentileSection";
import { HomePage } from "./components/HomePage";
import { CompensationPage } from "./components/CompensationPage";

export type Page = "home" | "service" | "team" | "responder" | "teamHealth" | "trends" | "compensation";

const TABS: { id: Page; label: string }[] = [
  { id: "home",         label: "Home" },
  { id: "service",      label: "Service Metrics" },
  { id: "team",         label: "Team Metrics" },
  { id: "responder",    label: "Responder" },
  { id: "teamHealth",   label: "Team Health" },
  { id: "trends",       label: "Trends" },
  { id: "compensation", label: "Compensation" },
];

function getDefaultSince(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0]!;
}

function getToday(): string {
  return new Date().toISOString().split("T")[0]!;
}

function detectTheme(): "dark" | "light" {
  const param = new URLSearchParams(window.location.search).get("theme");
  if (param === "dark") return "dark";
  if (param === "light") return "light";
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Operations Intelligence", version: "3.0.0" },
    capabilities: {},
  });
  const mockMode = import.meta.env.VITE_MOCK === "true";

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [page, setPage] = useState<Page>("home");
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [selectedTeam, setSelectedTeam] = useState<string>("");

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
    if (!app && !mockMode) return;
    setLoading(true);
    setError(null);
    try {
      const d = await fetchOpsData(
        app ?? ({} as any),
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

  const displayError = mockMode ? null : (connectionError?.message ?? error);

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="app-header">
        <span className="pd-icon"><PagerDutyLogo size={22} /></span>
        <h1>Operations Intelligence</h1>
        <div className="header-spacer" />
        <div className="header-controls">
          <select
            className="ctrl-btn"
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.currentTarget.value)}
          >
            <option value="">All teams</option>
            {(data?.teams ?? []).map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          <input
            type="date"
            className="ctrl-btn"
            value={since}
            onChange={(e) => setSince(e.currentTarget.value)}
          />
          <input
            type="date"
            className="ctrl-btn"
            value={until}
            onChange={(e) => setUntil(e.currentTarget.value)}
          />
          <button className="btn btn-primary btn-sm" onClick={load} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>
      </header>

      {/* ── Tab nav ── */}
      <nav className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn${page === tab.id ? " tab-active" : ""}`}
            onClick={() => setPage(tab.id)}
          >
            {page === tab.id && <span className="tab-dot" />}
            {tab.label}
          </button>
        ))}
      </nav>

      {/* ── Error banner ── */}
      {displayError && <div className="error-state">{displayError}</div>}

      {/* ── Loading ── */}
      {loading && !data && <div className="loading">Loading operational data…</div>}

      {/* ── Page content ── */}
      {(!loading || data) ? (
        <>
          {page === "home" && <HomePage onNavigate={setPage} />}

          {page === "service" && data && (
            <div className="body">
              <SummaryCards data={data} />
              <PercentileSection aggregated={data.aggregated} />
              <ServiceBreakdown metrics={data.serviceMetrics} />
            </div>
          )}

          {page === "team" && data && (
            <div className="body">
              <TeamBreakdown metrics={data.teamMetrics} />
            </div>
          )}

          {page === "responder" && data && (
            <div className="body">
              <ResponderLoad metrics={data.responderMetrics} />
            </div>
          )}

          {page === "teamHealth" && data && (
            <TeamHealth metrics={data.responderMetrics} teamMetrics={data.teamMetrics} />
          )}

          {page === "trends" && data && (
            <TrendsTab trendsData={data.trendsData} />
          )}

          {page === "compensation" && data && (
            <CompensationPage metrics={data.responderMetrics} />
          )}

          {page !== "home" && !data && !loading && (
            <div className="empty-state">No data — adjust date range and refresh.</div>
          )}
        </>
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
