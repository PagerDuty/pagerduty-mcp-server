// src/components/ComplianceTab.tsx

import type { ComplianceRecord } from "../compliance";
import type { ComplianceConfig } from "../config";
import { InfoIcon } from "./InfoIcon";

interface Props {
  records: ComplianceRecord[];
  config: ComplianceConfig;
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

export function ComplianceTab({ records, config }: Props) {
  const overCount = records.filter((r) => r.complianceStatus === "over").length;
  const withinCapsCount = records.length - overCount;

  const showConsecDays = config.maxConsecutiveDays > 0;
  const showConsecHours = config.maxConsecutiveHours > 0;
  const showRest = config.mandatoryRestHours > 0;

  return (
    <div className="compliance-tab">
      {overCount > 0 && (
        <div className="compliance-violation-banner">
          ⚠ <strong>{overCount} user{overCount > 1 ? "s" : ""}</strong> have exceeded configured oncall caps this period.
        </div>
      )}

      <div className="compliance-stats-bar">
        <div className="compliance-stat-pill compliance-stat-pill--ok">
          <span className="compliance-stat-number">{withinCapsCount}</span>
          <span className="compliance-stat-label">Within Caps</span>
        </div>
        <div className={`compliance-stat-pill${overCount > 0 ? " compliance-stat-pill--over" : ""}`}>
          <span className="compliance-stat-number">{overCount}</span>
          <span className="compliance-stat-label">Violations</span>
        </div>
        <div className="compliance-stat-pill">
          <span className="compliance-stat-number">{config.periodHoursCap}h</span>
          <span className="compliance-stat-label">
            Period Cap <InfoIcon text="Maximum total scheduled oncall hours per user for the selected date range. Configured in Settings." />
          </span>
        </div>
        <div className="compliance-stat-pill">
          <span className="compliance-stat-number">{config.periodOutsideHoursCap}h</span>
          <span className="compliance-stat-label">
            Outside Cap <InfoIcon text="Maximum oncall hours outside business hours per user for the selected date range. Configured in Settings." />
          </span>
        </div>
        {showConsecDays && (
          <div className="compliance-stat-pill">
            <span className="compliance-stat-number">{config.maxConsecutiveDays}d</span>
            <span className="compliance-stat-label">
              Max Consec. Days <InfoIcon text="Maximum consecutive calendar days with on-call coverage." />
            </span>
          </div>
        )}
        {showConsecHours && (
          <div className="compliance-stat-pill">
            <span className="compliance-stat-number">{config.maxConsecutiveHours}h</span>
            <span className="compliance-stat-label">
              Max Consec. Hrs <InfoIcon text="Maximum length of an unbroken on-call shift." />
            </span>
          </div>
        )}
        {showRest && (
          <div className="compliance-stat-pill">
            <span className="compliance-stat-number">{config.mandatoryRestHours}h</span>
            <span className="compliance-stat-label">
              Min Rest <InfoIcon text="Minimum required gap between consecutive on-call shifts." />
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
              <th style={{ textAlign: "right" }}>Sched Hours</th>
              <th>
                vs. Period Cap
                <InfoIcon text={`Cap: ${config.periodHoursCap}h. Progress bar shows usage. Red = over cap, amber = within ${Math.round(config.nearLimitThreshold * 100)}% of cap.`} />
              </th>
              <th style={{ textAlign: "right" }}>Outside Hrs</th>
              <th>
                vs. Outside Cap
                <InfoIcon text={`Cap: ${config.periodOutsideHoursCap}h. Red = over cap, amber = within ${Math.round(config.nearLimitThreshold * 100)}% of cap.`} />
              </th>
              {showConsecDays && (
                <th>
                  Consec. Days
                  <InfoIcon text={`Max ${config.maxConsecutiveDays} consecutive calendar days on-call.`} />
                </th>
              )}
              {showConsecHours && (
                <th>
                  Consec. Hrs
                  <InfoIcon text={`Max ${config.maxConsecutiveHours}h unbroken on-call shift.`} />
                </th>
              )}
              {showRest && (
                <th style={{ textAlign: "center" }}>
                  Rest Period
                  <InfoIcon text={`Min ${config.mandatoryRestHours}h gap between consecutive shifts.`} />
                </th>
              )}
              <th style={{ textAlign: "center" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.userId} className={r.complianceStatus === "over" ? "compliance-row--over" : ""}>
                <td>{r.userName}</td>
                <td style={{ color: "var(--text-muted)" }}>
                  <TeamCell teamName={r.teamName} />
                </td>
                <td className="num-cell" style={{ color: r.complianceStatus === "over" ? "var(--impacted-high)" : undefined }}>
                  {r.scheduledHours.toFixed(1)}h
                </td>
                <td>
                  <ProgressBar pct={r.hoursCapPct} status={r.hoursCapPct > 1 ? "over" : r.hoursCapPct >= config.nearLimitThreshold ? "near" : "ok"} />
                  <div className="compliance-bar-label">
                    {r.scheduledHours.toFixed(1)}/{config.periodHoursCap}h
                    {r.hoursCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{(r.scheduledHours - config.periodHoursCap).toFixed(1)}h over)</span>}
                    {r.hoursCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.hoursCapPct * 100)}%)</span>}
                  </div>
                </td>
                <td className="num-cell">{r.outsideHours.toFixed(1)}h</td>
                <td>
                  <ProgressBar pct={r.outsideCapPct} status={r.outsideCapPct > 1 ? "over" : r.outsideCapPct >= config.nearLimitThreshold ? "near" : "ok"} />
                  <div className="compliance-bar-label">
                    {r.outsideHours.toFixed(1)}/{config.periodOutsideHoursCap}h
                    {r.outsideCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{(r.outsideHours - config.periodOutsideHoursCap).toFixed(1)}h over)</span>}
                    {r.outsideCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.outsideCapPct * 100)}%)</span>}
                  </div>
                </td>
                {showConsecDays && (
                  <td>
                    <ProgressBar pct={r.consecutiveDaysPct} status={r.consecutiveDaysPct > 1 ? "over" : r.consecutiveDaysPct >= config.nearLimitThreshold ? "near" : "ok"} />
                    <div className="compliance-bar-label">
                      {r.maxConsecutiveOnCallDays}/{config.maxConsecutiveDays}d
                      {r.consecutiveDaysPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (over)</span>}
                      {r.consecutiveDaysPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.consecutiveDaysPct * 100)}%)</span>}
                    </div>
                  </td>
                )}
                {showConsecHours && (
                  <td>
                    <ProgressBar pct={r.consecutiveHoursPct} status={r.consecutiveHoursPct > 1 ? "over" : r.consecutiveHoursPct >= config.nearLimitThreshold ? "near" : "ok"} />
                    <div className="compliance-bar-label">
                      {r.maxConsecutiveOnCallHours.toFixed(1)}/{config.maxConsecutiveHours}h
                      {r.consecutiveHoursPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (over)</span>}
                      {r.consecutiveHoursPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.consecutiveHoursPct * 100)}%)</span>}
                    </div>
                  </td>
                )}
                {showRest && (
                  <td style={{ textAlign: "center" }}>
                    {r.minRestHours >= 999
                      ? <span className="compliance-badge compliance-badge--ok">N/A</span>
                      : r.restViolation
                        ? <span className="compliance-badge compliance-badge--over">⚠ {r.minRestHours.toFixed(1)}h rest</span>
                        : <span className="compliance-badge compliance-badge--ok">✓ {r.minRestHours.toFixed(1)}h rest</span>
                    }
                  </td>
                )}
                <td style={{ textAlign: "center" }}>
                  <StatusBadge status={r.complianceStatus} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
