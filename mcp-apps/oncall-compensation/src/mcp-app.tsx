/**
 * Oncall Compensation & Compliance — React App
 */

import type { App as McpApp } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchCompensationData } from "./api";
import type { CompensationData, UserCompensationRecord } from "./api";
import { computeOutsideHoursMetrics } from "./businessHours";
import { loadSettings, saveSettings } from "./config";
import type { AllSettings } from "./config";
import { computeEstimatedPay } from "./compensation";
import { deriveComplianceRecords } from "./compliance";
import { computeFairnessData } from "./fairness";
import { TabBar } from "./components/TabBar";
import type { TabId } from "./components/TabBar";
import { CompensationTab } from "./components/CompensationTab";
import { ComplianceTab } from "./components/ComplianceTab";
import { FairnessTab } from "./components/FairnessTab";
import { SettingsTab } from "./components/SettingsTab";
import { UserDetailModal } from "./components/UserDetailModal";
import type { SortKey } from "./components/CompensationTable";

function getDefaultSince(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0]!;
}

function getToday(): string {
  return new Date().toISOString().split("T")[0]!;
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Oncall Compensation & Compliance", version: "2.0.0" },
    capabilities: {},
  });

  const [data, setData] = useState<CompensationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [activeTab, setActiveTab] = useState<TabId>("compensation");
  const [settings, setSettings] = useState<AllSettings>(loadSettings);

  // Compensation tab state
  const [search, setSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("");
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("scheduledHours");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [visibleCols, setVisibleCols] = useState<Set<SortKey>>(
    () =>
      new Set<SortKey>([
        "scheduledHours",
        "incidentCount",
        "interruptionRate",
        "offHourInterruptions",
        "sleepHourInterruptions",
        "outsideHours",
        "weekendHours",
        "uniquePeriodsOutside",
        "estimatedPay",
      ]),
  );
  const [colPickerOpen, setColPickerOpen] = useState(false);
  const [showSummary, setShowSummary] = useState(true);
  const [displayMode, setDisplayMode] = useState<"inline" | "fullscreen" | "pip">("inline");

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if (ctx.displayMode) setDisplayMode(ctx.displayMode);
    };
  }, [app]);

  useEffect(() => {
    if (!app) return;
    let cancelled = false;

    async function load(appInstance: McpApp) {
      setLoading(true);
      setError(null);
      setSelectedUserId(null);
      try {
        const result = await fetchCompensationData(
          appInstance,
          `${since}T00:00:00Z`,
          `${until}T23:59:59Z`,
        );
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          console.error("[Compensation] Failed to load:", err);
          setError(err instanceof Error ? err.message : "Failed to load compensation data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load(app);
    return () => { cancelled = true; };
  }, [app, since, until]);

  // Layer 1: enrich with outside-hours metrics (estimatedPay set by Layer 2)
  const enrichedRecords = useMemo((): UserCompensationRecord[] => {
    if (!data) return [];
    return data.records.map((r) => {
      if (r.oncallShifts.length === 0) return r;
      const m = computeOutsideHoursMetrics(r.oncallShifts, settings.businessHours);
      return {
        ...r,
        outsideHours: m.totalOutsideHours,
        weekendHours: m.totalWeekendHours,
        holidayHours: m.totalHolidayHours,
        maxConsecutiveOutsideHours: m.maxConsecutiveOutsideHours,
        uniquePeriodsOutside: m.uniquePeriodsOutside,
      };
    });
  }, [data, settings.businessHours]);

  // Layer 2: compute estimated pay
  const compensatedRecords = useMemo(
    () => enrichedRecords.map((r) => ({ ...r, estimatedPay: computeEstimatedPay(r, settings.pay) })),
    [enrichedRecords, settings.pay],
  );

  // Layer 3: compliance records
  const complianceRecords = useMemo(
    () => deriveComplianceRecords(compensatedRecords, settings.compliance),
    [compensatedRecords, settings.compliance],
  );

  // Layer 4: fairness data
  const fairnessData = useMemo(
    () => computeFairnessData(compensatedRecords, settings.fairness),
    [compensatedRecords, settings.fairness],
  );

  const handleSort = (key: SortKey) => {
    if (key === sortKey) setSortDir((d) => (d === "desc" ? "asc" : "desc"));
    else { setSortKey(key); setSortDir("desc"); }
  };

  const filteredRecords = useMemo((): UserCompensationRecord[] => {
    const q = search.toLowerCase().trim();
    let list = compensatedRecords;
    if (q) {
      list = list.filter(
        (r) => r.userName.toLowerCase().includes(q) || (r.teamName?.toLowerCase().includes(q) ?? false),
      );
    }
    if (teamFilter) list = list.filter((r) => r.teamIds.includes(teamFilter));
    return [...list].sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      if (sortKey === "userName") return a.userName.localeCompare(b.userName) * dir;
      return ((a[sortKey] as number) - (b[sortKey] as number)) * dir;
    });
  }, [compensatedRecords, search, teamFilter, sortKey, sortDir]);

  const selectedRecord = selectedUserId
    ? compensatedRecords.find((r) => r.userId === selectedUserId) ?? null
    : null;

  const displayError = connectionError?.message ?? error;

  const handleSaveSettings = (s: AllSettings) => {
    setSettings(s);
    saveSettings(s);
  };

  const doRefresh = () => {
    const s = since;
    setSince("");
    setTimeout(() => setSince(s), 0);
  };

  return (
    <div className="app" data-theme="dark">
      <header className="header">
        <div className="header-left">
          <PagerDutyIcon />
          <div>
            <div className="header-title">Oncall Compensation &amp; Compliance</div>
            <div className="header-subtitle">
              {data
                ? `${data.records.length} user${data.records.length !== 1 ? "s" : ""}`
                : loading ? "Loading…" : "No data"}
            </div>
          </div>
        </div>

        <div className="header-dates">
          <span className="header-date-label">From</span>
          <input
            type="date"
            className="header-date-input"
            value={since}
            max={until}
            onChange={(e) => setSince(e.target.value)}
            disabled={loading}
          />
          <span className="header-date-label">To</span>
          <input
            type="date"
            className="header-date-input"
            value={until}
            min={since}
            max={getToday()}
            onChange={(e) => setUntil(e.target.value)}
            disabled={loading}
          />
          <button className="btn-refresh-header" disabled={loading} onClick={doRefresh}>
            <span className="pd-dot" />
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>

        <button
          className="btn-expand"
          onClick={async () => {
            if (!app) return;
            await app.requestDisplayMode({
              mode: displayMode === "fullscreen" ? "inline" : "fullscreen",
            });
          }}
          title={displayMode === "fullscreen" ? "Exit fullscreen" : "Expand to fullscreen"}
        >
          {displayMode === "fullscreen" ? "⤡" : "⤢"}
        </button>
      </header>

      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Team/search controls — compensation tab only */}
      {activeTab === "compensation" && (
        <div className="controls">
          {(data?.teams.length ?? 0) > 0 && (
            <select
              value={teamFilter}
              onChange={(e) => { setTeamFilter(e.target.value); setSelectedUserId(null); }}
              disabled={loading}
            >
              <option value="">All teams</option>
              {(data?.teams ?? []).map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          )}
          <div className="search-wrap">
            <SearchIcon />
            <input
              type="text"
              placeholder="Search users or teams…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>
      )}

      <div className="main-content">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner" />
            <span>Loading data…</span>
          </div>
        )}

        {!loading && displayError && <div className="error-banner">⚠ {displayError}</div>}

        {!loading && (
          <>
            {activeTab === "compensation" && (
              <CompensationTab
                records={filteredRecords}
                selectedId={selectedUserId}
                onSelect={(id) => setSelectedUserId((cur) => (cur === id ? null : id))}
                sortKey={sortKey}
                sortDir={sortDir}
                onSort={handleSort}
                visibleCols={visibleCols}
                onVisibleColsChange={setVisibleCols}
                colPickerOpen={colPickerOpen}
                onColPickerToggle={() => setColPickerOpen((o) => !o)}
                onColPickerClose={() => setColPickerOpen(false)}
                showSummary={showSummary}
                onToggleSummary={() => setShowSummary((s) => !s)}
              />
            )}
            {activeTab === "compliance" && (
              <ComplianceTab records={complianceRecords} config={settings.compliance} />
            )}
            {activeTab === "fairness" && (
              <FairnessTab data={fairnessData} outlierMultiplier={settings.fairness.outlierMultiplier} />
            )}
            {activeTab === "settings" && (
              <SettingsTab settings={settings} onSave={handleSaveSettings} />
            )}
          </>
        )}
      </div>

      {selectedRecord && (
        <UserDetailModal record={selectedRecord} onClose={() => setSelectedUserId(null)} />
      )}
    </div>
  );
}

function SearchIcon() {
  return (
    <svg className="search-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="6.5" cy="6.5" r="4" />
      <path d="M11 11l3 3" strokeLinecap="round" />
    </svg>
  );
}

function PagerDutyIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="16" fill="#06AC38" />
      <path
        d="M35 25h18c10 0 18 7 18 17s-8 17-18 17H47v16H35V25zm12 24h5c4.5 0 7-2.5 7-7s-2.5-7-7-7H47v14z"
        fill="white"
      />
    </svg>
  );
}

const container = document.getElementById("root");
if (container) {
  createRoot(container).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
