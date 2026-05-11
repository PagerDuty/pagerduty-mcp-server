// src/components/FairnessTab.tsx

import type { FairnessRecord } from "../fairness";
import type { FairnessConfig } from "../config";
import { InfoIcon } from "./InfoIcon";

interface Props {
  records: FairnessRecord[];
  config: FairnessConfig;
}

function TeamCell({ teamName }: { teamName?: string }) {
  if (!teamName) return <span>—</span>;
  const teams = teamName.split(", ");
  if (teams.length <= 1) return <span>{teamName}</span>;
  const [first, ...rest] = teams;
  return (
    <span className="team-cell">
      {first}
      <span className="team-overflow-badge" title={rest.join(", ")}>+{rest.length}</span>
    </span>
  );
}

function ProgressBar({ pct, status }: { pct: number; status: "ok" | "near" | "over" }) {
  const fillPct = Math.min(pct * 100, 100);
  const color = status === "over" ? "var(--impacted-high)" : status === "near" ? "var(--ooh-orange)" : "var(--pd-green)";
  return (
    <div className="compliance-bar-wrap">
      <div className="compliance-bar-track">
        <div className="compliance-bar-fill" style={{ width: `${fillPct}%`, background: color }} />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: "ok" | "near" | "over" }) {
  if (status === "over") return <span className="compliance-badge compliance-badge--over">⚠ OVER CAP</span>;
  if (status === "near") return <span className="compliance-badge compliance-badge--near">⚡ NEAR</span>;
  return <span className="compliance-badge compliance-badge--ok">✓ OK</span>;
}

export function FairnessTab({ records, config }: Props) {
  const overCount = records.filter((r) => r.fairnessStatus === "over").length;
  const withinCount = records.length - overCount;

  const showWeekends = config.maxWeekendsPerPeriod > 0;
  const showHolidays = config.maxHolidaysPerPeriod > 0;
  const showOoh = config.maxOohPeriodsPerPeriod > 0;

  const weekendViolations = showWeekends ? records.filter((r) => r.weekendCapPct > 1).length : 0;
  const holidayViolations = showHolidays ? records.filter((r) => r.holidayCapPct > 1).length : 0;
  const oohViolations = showOoh ? records.filter((r) => r.oohPeriodsCapPct > 1).length : 0;

  return (
    <div className="compliance-tab">
      {overCount > 0 && (
        <div className="compliance-violation-banner">
          ⚠ <strong>{overCount} user{overCount > 1 ? "s" : ""}</strong> have exceeded configured fairness limits this period.
        </div>
      )}

      <div className="compliance-stats-bar">
        <div className="compliance-stat-pill compliance-stat-pill--ok">
          <span className="compliance-stat-number">{withinCount}</span>
          <span className="compliance-stat-label">Within Limits</span>
        </div>
        <div className={`compliance-stat-pill${overCount > 0 ? " compliance-stat-pill--over" : ""}`}>
          <span className="compliance-stat-number">{overCount}</span>
          <span className="compliance-stat-label">Violations</span>
        </div>
        {showWeekends && (
          <div className={`compliance-stat-pill${weekendViolations > 0 ? " compliance-stat-pill--over" : ""}`}>
            <span className="compliance-stat-number">{weekendViolations}</span>
            <span className="compliance-stat-label">
              Weekend Violations <InfoIcon text={`Users with more than ${config.maxWeekendsPerPeriod} weekend${config.maxWeekendsPerPeriod !== 1 ? "s" : ""} on-call.`} />
            </span>
          </div>
        )}
        {showHolidays && (
          <div className={`compliance-stat-pill${holidayViolations > 0 ? " compliance-stat-pill--over" : ""}`}>
            <span className="compliance-stat-number">{holidayViolations}</span>
            <span className="compliance-stat-label">
              Holiday Violations <InfoIcon text={`Users with more than ${config.maxHolidaysPerPeriod} holiday${config.maxHolidaysPerPeriod !== 1 ? "s" : ""} on-call.`} />
            </span>
          </div>
        )}
        {showOoh && (
          <div className={`compliance-stat-pill${oohViolations > 0 ? " compliance-stat-pill--over" : ""}`}>
            <span className="compliance-stat-number">{oohViolations}</span>
            <span className="compliance-stat-label">
              OOH Period Violations <InfoIcon text={`Users with more than ${config.maxOohPeriodsPerPeriod} outside-hours on-call blocks.`} />
            </span>
          </div>
        )}
      </div>

      <div className="table-area">
        <table className="comp-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Team</th>
              {showWeekends && (
                <th>
                  Weekends vs Cap
                  <InfoIcon text={`Cap: ${config.maxWeekendsPerPeriod} weekends. Number of distinct weekends (Sat or Sun) with any on-call coverage.`} />
                </th>
              )}
              {showHolidays && (
                <th>
                  Holidays vs Cap
                  <InfoIcon text={`Cap: ${config.maxHolidaysPerPeriod} holidays. Number of distinct holiday dates with any on-call coverage.`} />
                </th>
              )}
              {showOoh && (
                <th>
                  OOH Periods vs Cap
                  <InfoIcon text={`Cap: ${config.maxOohPeriodsPerPeriod} periods. Number of distinct outside-business-hours on-call blocks.`} />
                </th>
              )}
              <th style={{ textAlign: "center" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.userId} className={r.fairnessStatus === "over" ? "compliance-row--over" : ""}>
                <td>{r.userName}</td>
                <td style={{ color: "var(--text-muted)" }}>
                  <TeamCell teamName={r.teamName} />
                </td>
                {showWeekends && (
                  <td>
                    <ProgressBar pct={r.weekendCapPct} status={r.weekendCapPct > 1 ? "over" : r.weekendCapPct >= config.nearLimitThreshold ? "near" : "ok"} />
                    <div className="compliance-bar-label">
                      {r.weekendPeriodCount}/{config.maxWeekendsPerPeriod} weekends
                      {r.weekendCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{r.weekendPeriodCount - config.maxWeekendsPerPeriod} over)</span>}
                      {r.weekendCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.weekendCapPct * 100)}%)</span>}
                    </div>
                  </td>
                )}
                {showHolidays && (
                  <td>
                    <ProgressBar pct={r.holidayCapPct} status={r.holidayCapPct > 1 ? "over" : r.holidayCapPct >= config.nearLimitThreshold ? "near" : "ok"} />
                    <div className="compliance-bar-label">
                      {r.holidayCount}/{config.maxHolidaysPerPeriod} holidays
                      {r.holidayCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{r.holidayCount - config.maxHolidaysPerPeriod} over)</span>}
                      {r.holidayCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.holidayCapPct * 100)}%)</span>}
                    </div>
                  </td>
                )}
                {showOoh && (
                  <td>
                    <ProgressBar pct={r.oohPeriodsCapPct} status={r.oohPeriodsCapPct > 1 ? "over" : r.oohPeriodsCapPct >= config.nearLimitThreshold ? "near" : "ok"} />
                    <div className="compliance-bar-label">
                      {r.uniquePeriodsOutside}/{config.maxOohPeriodsPerPeriod} periods
                      {r.oohPeriodsCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{r.uniquePeriodsOutside - config.maxOohPeriodsPerPeriod} over)</span>}
                      {r.oohPeriodsCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.oohPeriodsCapPct * 100)}%)</span>}
                    </div>
                  </td>
                )}
                <td style={{ textAlign: "center" }}>
                  <StatusBadge status={r.fairnessStatus} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
