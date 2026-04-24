import { useState, useMemo } from "react";
import type { ResponderMetric } from "../api";
import { fmtMin } from "../utils";
import {
  type BusinessHoursConfig,
  type OutsideHoursMetrics,
  computeOutsideHoursMetrics,
  defaultBHConfig,
} from "../businessHours";

interface CompensationPageProps {
  metrics: ResponderMetric[];
}

interface EnrichedMetric extends ResponderMetric {
  outside: OutsideHoursMetrics;
}

function fmtHours(h: number): string {
  if (h === 0) return "0h";
  const rounded = Math.round(h * 10) / 10;
  return `${rounded}h`;
}

function parseHolidays(raw: string): Set<string> {
  const result = new Set<string>();
  for (const line of raw.split(/[\n,]+/)) {
    const t = line.trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(t)) result.add(t);
  }
  return result;
}

const TIMEZONES = [
  "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
  "America/Sao_Paulo", "Europe/London", "Europe/Paris", "Europe/Berlin",
  "Asia/Tokyo", "Asia/Singapore", "Asia/Kolkata", "Australia/Sydney", "UTC",
];

export function CompensationPage({ metrics }: CompensationPageProps) {
  const [configOpen, setConfigOpen] = useState(false);
  const [startHour, setStartHour] = useState(9);
  const [endHour, setEndHour] = useState(18);
  const [timezone, setTimezone] = useState(
    () => defaultBHConfig().timezone
  );
  const [holidayText, setHolidayText] = useState("");

  const bhConfig: BusinessHoursConfig = useMemo(() => ({
    startHour,
    endHour,
    workDays: new Set([1, 2, 3, 4, 5]),
    holidays: parseHolidays(holidayText),
    timezone,
  }), [startHour, endHour, timezone, holidayText]);

  const enriched: EnrichedMetric[] = useMemo(() =>
    metrics.map((r) => ({
      ...r,
      outside: computeOutsideHoursMetrics(r.oncallShifts, bhConfig),
    })),
    [metrics, bhConfig]
  );

  if (enriched.length === 0) {
    return <div className="comp-empty">No responder data available for this period.</div>;
  }

  const sorted = [...enriched].sort((a, b) => b.onCallHours - a.onCallHours);

  const totalOnCallHours = metrics.reduce((s, r) => s + r.onCallHours, 0);
  const avgOnCallHours = Math.round((totalOnCallHours / metrics.length) * 10) / 10;
  const totalSleepInt = metrics.reduce((s, r) => s + r.sleepInterruptions, 0);
  const highRiskCount = metrics.filter((r) => r.riskLevel === "high").length;
  const totalOutside = enriched.reduce((s, r) => s + r.outside.totalOutsideHours, 0);

  return (
    <div className="comp-page">
      {/* KPI bar */}
      <div className="kpi-bar">
        <div className="kpi-cell kpi-ok">
          <div className="kpi-label">Responders</div>
          <div className="kpi-value">{metrics.length}</div>
          <div className="kpi-sub">with on-call data</div>
        </div>
        <div className="kpi-cell">
          <div className="kpi-label">Total On-Call</div>
          <div className="kpi-value">{fmtHours(totalOnCallHours)}</div>
          <div className="kpi-sub">hours this period</div>
        </div>
        <div className="kpi-cell">
          <div className="kpi-label">Avg Per Responder</div>
          <div className="kpi-value">{fmtHours(avgOnCallHours)}</div>
          <div className="kpi-sub">on-call hours</div>
        </div>
        <div className={`kpi-cell${totalOutside > 0 ? " kpi-warn" : " kpi-ok"}`}>
          <div className="kpi-label">Outside Business Hrs</div>
          <div className={`kpi-value${totalOutside > 0 ? " warn" : ""}`}>{fmtHours(Math.round(totalOutside * 10) / 10)}</div>
          <div className="kpi-sub">total across team</div>
        </div>
        <div className={`kpi-cell${totalSleepInt > 0 ? " kpi-warn" : " kpi-ok"}`}>
          <div className="kpi-label">Sleep Interruptions</div>
          <div className={`kpi-value${totalSleepInt > 0 ? " warn" : ""}`}>{totalSleepInt}</div>
          <div className="kpi-sub">total this period</div>
        </div>
        <div className={`kpi-cell${highRiskCount > 0 ? " kpi-warn" : " kpi-ok"}`}>
          <div className="kpi-label">High Risk</div>
          <div className={`kpi-value${highRiskCount > 0 ? " warn" : ""}`}>{highRiskCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
      </div>

      {/* Business hours config */}
      <div className="comp-bh-bar">
        <button
          className="comp-bh-toggle"
          onClick={() => setConfigOpen((o) => !o)}
        >
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="8" cy="8" r="3"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M3.05 12.95l1.41-1.41M11.54 4.46l1.41-1.41"/>
          </svg>
          Business Hours Config
          <span className="comp-bh-summary">
            {String(startHour).padStart(2, "0")}:00–{String(endHour).padStart(2, "0")}:00 · Mon–Fri · {timezone}
            {parseHolidays(holidayText).size > 0 && ` · ${parseHolidays(holidayText).size} holidays`}
          </span>
          <span className="comp-bh-chevron">{configOpen ? "▲" : "▼"}</span>
        </button>

        {configOpen && (
          <div className="comp-bh-panel">
            <div className="comp-bh-row">
              <label className="comp-bh-label">Business hours</label>
              <div className="comp-bh-fields">
                <select
                  className="ctrl-btn"
                  value={startHour}
                  onChange={(e) => setStartHour(Number(e.currentTarget.value))}
                >
                  {Array.from({ length: 24 }, (_, i) => (
                    <option key={i} value={i}>{String(i).padStart(2, "0")}:00</option>
                  ))}
                </select>
                <span className="comp-bh-sep">to</span>
                <select
                  className="ctrl-btn"
                  value={endHour}
                  onChange={(e) => setEndHour(Number(e.currentTarget.value))}
                >
                  {Array.from({ length: 24 }, (_, i) => (
                    <option key={i} value={i}>{String(i).padStart(2, "0")}:00</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="comp-bh-row">
              <label className="comp-bh-label">Timezone</label>
              <select
                className="ctrl-btn"
                value={timezone}
                onChange={(e) => setTimezone(e.currentTarget.value)}
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            </div>
            <div className="comp-bh-row comp-bh-row--top">
              <label className="comp-bh-label">Holidays</label>
              <div className="comp-bh-fields comp-bh-fields--col">
                <textarea
                  className="comp-bh-textarea"
                  placeholder={"2026-01-01\n2026-12-25\n2026-07-04"}
                  value={holidayText}
                  onChange={(e) => setHolidayText(e.currentTarget.value)}
                  rows={3}
                />
                <span className="comp-bh-hint">One date per line (YYYY-MM-DD) or comma-separated</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="analytics-section">
        <div className="section-title">
          Responder On-Call Summary
          <span className="section-count">{metrics.length}</span>
        </div>
        <table className="analytics-table comp-table">
          <thead>
            <tr>
              <th>Responder</th>
              <th className="col-num">Total Hrs</th>
              <th className="col-num">L1 Hrs</th>
              <th className="col-num">L2+ Hrs</th>
              <th className="col-num">Outside Hrs</th>
              <th className="col-num">Weekend Hrs</th>
              <th className="col-num">Holiday Hrs</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">Sleep Int.</th>
              <th className="col-num">Off-Hr Int.</th>
              <th className="col-num">Engaged Time</th>
              <th className="col-num">Risk</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r) => (
              <tr key={r.id} className={r.riskLevel !== "low" ? `row-risk-${r.riskLevel}` : ""}>
                <td className="col-name">
                  {r.name}
                  {r.teamName && <span className="kpi-sub"> · {r.teamName}</span>}
                </td>
                <td className="col-num col-mono">{fmtHours(r.onCallHours)}</td>
                <td className="col-num col-mono">{fmtHours(r.onCallHoursL1)}</td>
                <td className="col-num col-mono">{fmtHours(r.onCallHoursL2Plus)}</td>
                <td className={`col-num col-mono${r.outside.totalOutsideHours > 0 ? " col-warn" : ""}`}>
                  {fmtHours(r.outside.totalOutsideHours)}
                </td>
                <td className="col-num col-mono">{fmtHours(r.outside.totalWeekendHours)}</td>
                <td className={`col-num col-mono${r.outside.totalHolidayHours > 0 ? " col-warn" : ""}`}>
                  {fmtHours(r.outside.totalHolidayHours)}
                </td>
                <td className="col-num">{r.totalIncidents}</td>
                <td className={`col-num${r.sleepInterruptions > 0 ? " col-warn" : " col-ok"}`}>
                  {r.sleepInterruptions}
                </td>
                <td className="col-num">{r.offHourInterruptions}</td>
                <td className="col-num col-mono">{fmtMin(r.engagedMinutes)}</td>
                <td className="col-num">
                  <span className={`risk-badge risk-${r.riskLevel}`}>
                    {r.riskLevel.charAt(0).toUpperCase() + r.riskLevel.slice(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
