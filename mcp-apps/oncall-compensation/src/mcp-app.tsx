/**
 * Oncall Compensation Report - React App
 */

import type { App as McpApp } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchCompensationData } from "./api";
import type { CompensationData, UserCompensationRecord } from "./api";
import { computeOutsideHoursMetrics, defaultBHConfig } from "./businessHours";
import type { BusinessHoursConfig } from "./businessHours";
import { CompensationTable } from "./components/CompensationTable";
import type { SortKey } from "./components/CompensationTable";
import { ColumnPicker } from "./components/ColumnPicker";
import { SummaryCards } from "./components/SummaryCards";
import { UserDetailModal } from "./components/UserDetailModal";
import { BusinessHoursConfig as BusinessHoursConfigPanel } from "./components/BusinessHoursConfig";

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
    appInfo: { name: "Oncall Compensation Report", version: "1.0.0" },
    capabilities: {},
  });

  const [data, setData] = useState<CompensationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
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
      ]),
  );
  const [colPickerOpen, setColPickerOpen] = useState(false);
  const [bhConfig, setBhConfig] = useState<BusinessHoursConfig>(defaultBHConfig);
  const [bhModalOpen, setBhModalOpen] = useState(false);
  const [showSummary, setShowSummary] = useState(true);

  useEffect(() => {
    if (!app) return;
    let cancelled = false;

    async function load(appInstance: McpApp) {
      setLoading(true);
      setError(null);
      setSelectedUserId(null);
      try {
        const sinceISO = `${since}T00:00:00Z`;
        const untilISO = `${until}T23:59:59Z`;
        const result = await fetchCompensationData(appInstance, sinceISO, untilISO);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) {
          console.error("[Compensation] Failed to load:", err);
          setError(
            err instanceof Error ? err.message : "Failed to load compensation data",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load(app);
    return () => {
      cancelled = true;
    };
  }, [app, since, until]);

  // Recompute outside-hours metrics whenever data or business hours config changes.
  // This runs entirely in the browser — no additional API calls needed.
  const enrichedRecords = useMemo((): UserCompensationRecord[] => {
    if (!data) return [];
    return data.records.map((r) => {
      if (r.oncallShifts.length === 0) return r;
      const m = computeOutsideHoursMetrics(r.oncallShifts, bhConfig);
      return {
        ...r,
        outsideHours: m.totalOutsideHours,
        weekendHours: m.totalWeekendHours,
        holidayHours: m.totalHolidayHours,
        maxConsecutiveOutsideHours: m.maxConsecutiveOutsideHours,
        uniquePeriodsOutside: m.uniquePeriodsOutside,
      };
    });
  }, [data, bhConfig]);

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((d) => (d === "desc" ? "asc" : "desc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const filteredRecords = useMemo((): UserCompensationRecord[] => {
    const q = search.toLowerCase().trim();
    let list = enrichedRecords;

    if (q) {
      list = list.filter(
        (r) =>
          r.userName.toLowerCase().includes(q) ||
          (r.teamName?.toLowerCase().includes(q) ?? false),
      );
    }

    if (teamFilter) {
      list = list.filter((r) => r.teamId === teamFilter);
    }

    return [...list].sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      if (sortKey === "userName") {
        return a.userName.localeCompare(b.userName) * dir;
      }
      return (a[sortKey] - b[sortKey]) * dir;
    });
  }, [enrichedRecords, search, teamFilter, sortKey, sortDir]);

  const selectedRecord = selectedUserId
    ? (enrichedRecords ?? []).find((r) => r.userId === selectedUserId) ?? null
    : null;

  const displayError = connectionError?.message ?? error;

  const doRefresh = () => {
    const s = since;
    setSince("");
    setTimeout(() => setSince(s), 0);
  };

  const hasShiftsData = (data?.records ?? []).some((r) => r.oncallShifts.length > 0);

  return (
    <div className="app" data-theme="dark">
      {/* Header — title + date range + refresh */}
      <header className="header">
        <div className="header-left">
          <PagerDutyIcon />
          <div>
            <div className="header-title">Oncall Compensation Report</div>
            <div className="header-subtitle">
              {data
                ? `${data.records.length} user${data.records.length !== 1 ? "s" : ""}`
                : loading
                  ? "Loading…"
                  : "No data"}
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
          <button
            className={["btn-bh-config", bhModalOpen ? "active" : ""].filter(Boolean).join(" ")}
            onClick={() => setBhModalOpen((o) => !o)}
            disabled={loading}
            title="Configure business hours"
          >
            ⚙ Business Hours
            {bhConfig.holidays.size > 0 && (
              <span className="bh-badge" style={{ marginLeft: 4 }}>
                {bhConfig.holidays.size}
              </span>
            )}
          </button>
        </div>

        <button
          className="btn-refresh-header"
          disabled={loading}
          onClick={doRefresh}
        >
          <span className="pd-dot" />
          {loading ? "Loading…" : "Refresh"}
        </button>
      </header>

      {/* Business Hours Config modal */}
      {bhModalOpen && (
        <div className="bh-modal-backdrop" onClick={() => setBhModalOpen(false)}>
          <div className="bh-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="bh-modal-header">
              <span className="bh-modal-title">Business Hours Configuration</span>
              <button className="btn-close" onClick={() => setBhModalOpen(false)}>×</button>
            </div>
            <BusinessHoursConfigPanel
              config={bhConfig}
              onChange={setBhConfig}
              showToggle={false}
            />
          </div>
        </div>
      )}

      {!hasShiftsData && !loading && data && (
        <div className="bh-no-shifts-warn">
          No on-call schedule data available for outside-hours metrics. Schedule data requires on-call entries in the selected date range.
        </div>
      )}

      {/* Controls — team filter + search */}
      <div className="controls">
        <button
          className={["btn-summary-toggle", showSummary ? "active" : ""].filter(Boolean).join(" ")}
          onClick={() => setShowSummary((s) => !s)}
          title={showSummary ? "Hide summary" : "Show summary"}
        >
          {showSummary ? "▲ Summary" : "▼ Summary"}
        </button>
        {(data?.teams.length ?? 0) > 0 && (
          <select
            value={teamFilter}
            onChange={(e) => {
              setTeamFilter(e.target.value);
              setSelectedUserId(null);
            }}
            disabled={loading}
          >
            <option value="">All teams</option>
            {(data?.teams ?? []).map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
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

      {/* Summary strip — cards + column picker */}
      {showSummary && <div className="summary-strip">
        <SummaryCards records={filteredRecords} />
        <div className="summary-actions">
          <div style={{ position: "relative" }}>
            <button
              className={["btn-col-picker", colPickerOpen ? "active" : ""].filter(Boolean).join(" ")}
              onClick={() => setColPickerOpen((o) => !o)}
              title="Show/hide columns"
            >
              ⊞ Columns
            </button>
            <ColumnPicker
              visibleCols={visibleCols}
              onChange={setVisibleCols}
              open={colPickerOpen}
              onClose={() => setColPickerOpen(false)}
            />
          </div>
        </div>
      </div>}

      {/* Main content */}
      <div className="main-content">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner" />
            <span>Loading compensation data…</span>
          </div>
        )}

        {!loading && displayError && (
          <div className="error-banner">⚠ {displayError}</div>
        )}

        {!loading && (
          <div className="table-area">
            <CompensationTable
              records={filteredRecords}
              selectedId={selectedUserId}
              onSelect={(id) =>
                setSelectedUserId((cur) => (cur === id ? null : id))
              }
              sortKey={sortKey}
              sortDir={sortDir}
              onSort={handleSort}
              visibleCols={visibleCols}
            />
          </div>
        )}
      </div>

      {/* User detail modal */}
      {selectedRecord && (
        <UserDetailModal
          record={selectedRecord}
          onClose={() => setSelectedUserId(null)}
        />
      )}
    </div>
  );
}

function SearchIcon() {
  return (
    <svg
      className="search-icon"
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <circle cx="6.5" cy="6.5" r="4" />
      <path d="M11 11l3 3" strokeLinecap="round" />
    </svg>
  );
}

function PagerDutyIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
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
