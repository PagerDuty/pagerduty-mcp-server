// src/components/ComplianceTab.tsx

import type { ComplianceRecord } from "../compliance";
import type { ComplianceConfig } from "../config";
import { InfoIcon } from "./InfoIcon";

interface Props {
  records: ComplianceRecord[];
  config: ComplianceConfig;
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
  const okCount = records.filter((r) => r.complianceStatus === "ok").length;

  return (
    <div className="compliance-tab">
      {overCount > 0 && (
        <div className="compliance-violation-banner">
          ⚠ <strong>{overCount} user{overCount > 1 ? "s" : ""}</strong> have exceeded configured oncall caps this period.
        </div>
      )}

      <div className="summary-cards" style={{ padding: "8px 16px" }}>
        <div className="summary-card">
          <div className="card-value" style={{ color: "var(--pd-green)" }}>{okCount}</div>
          <div className="card-label">Compliant</div>
          <div className="card-sub">users within caps</div>
        </div>
        <div className="summary-card" style={{ borderColor: overCount > 0 ? "var(--impacted-high-bg)" : undefined }}>
          <div className="card-value" style={{ color: overCount > 0 ? "var(--impacted-high)" : "var(--text-muted)" }}>{overCount}</div>
          <div className="card-label">Violations</div>
          <div className="card-sub">users over cap</div>
        </div>
        <div className="summary-card">
          <div className="card-value">{config.periodHoursCap}h</div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Period Total Cap
            <InfoIcon text="Maximum total scheduled oncall hours per user for the selected date range. Configured in Settings." />
          </div>
        </div>
        <div className="summary-card">
          <div className="card-value">{config.periodOutsideHoursCap}h</div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Outside-Hours Cap
            <InfoIcon text="Maximum oncall hours outside business hours per user for the selected date range. Configured in Settings." />
          </div>
        </div>
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
              <th style={{ textAlign: "center" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.userId} className={r.complianceStatus === "over" ? "compliance-row--over" : ""}>
                <td>{r.userName}</td>
                <td style={{ color: "var(--text-muted)" }}>{r.teamName ?? "—"}</td>
                <td className="num-cell" style={{ color: r.complianceStatus === "over" ? "var(--impacted-high)" : undefined }}>
                  {r.scheduledHours.toFixed(1)}h
                </td>
                <td>
                  <ProgressBar pct={r.hoursCapPct} status={r.complianceStatus} />
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
