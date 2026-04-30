// src/components/FairnessTab.tsx

import type { FairnessData } from "../fairness";
import { InfoIcon } from "./InfoIcon";

interface Props {
  data: FairnessData;
  outlierMultiplier: number;
}

export function FairnessTab({ data, outlierMultiplier }: Props) {
  const equityColor = (score: number) =>
    score >= 80 ? "var(--pd-green)" : score >= 60 ? "var(--ooh-orange)" : "var(--impacted-high)";

  return (
    <div className="fairness-tab">
      {/* Summary cards */}
      <div className="summary-cards" style={{ padding: "8px 16px" }}>
        <div className="summary-card">
          <div className="card-value">{data.globalAvgHours}h</div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Avg Hours / Person
            <InfoIcon text="Mean scheduled oncall hours across all users in the selected period." />
          </div>
        </div>
        <div className="summary-card">
          <div className="card-value" style={{ color: data.globalStdDev > data.globalAvgHours * 0.5 ? "var(--ooh-orange)" : "var(--text-primary)" }}>
            {data.globalStdDev}h
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Std Deviation
            <InfoIcon text="Standard deviation of scheduled hours across all users. High deviation = uneven distribution." />
          </div>
        </div>
        <div className="summary-card" style={{ borderColor: data.outliers.length > 0 ? "var(--impacted-high-bg)" : undefined }}>
          <div className="card-value" style={{ color: data.outliers.length > 0 ? "var(--impacted-high)" : "var(--text-muted)" }}>
            {data.outliers.length}
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Outliers
            <InfoIcon text={`Users carrying ≥ ${outlierMultiplier}× the global average oncall hours. Configurable in Settings.`} />
          </div>
          <div className="card-sub">&gt;{outlierMultiplier}× avg load</div>
        </div>
        <div className="summary-card">
          <div className="card-value" style={{ color: equityColor(data.globalEquityScore) }}>
            {data.globalEquityScore} / 100
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Equity Score
            <InfoIcon text="Equity Score = 100 − (std deviation ÷ mean × 100), capped 0–100. Score of 100 = perfectly equal distribution. Lower = higher variance in oncall burden." />
          </div>
        </div>
      </div>

      <div className="fairness-body">
        {/* Outlier cards */}
        {data.outliers.length > 0 && (
          <div className="fairness-outliers">
            <h4 className="fairness-section-title">
              ⚠ Outliers — carrying {outlierMultiplier}×+ average load
              <InfoIcon text={`These users have scheduled hours ≥ ${outlierMultiplier}× the global average of ${data.globalAvgHours}h.`} />
            </h4>
            <div className="outlier-cards">
              {data.outliers.map((o) => (
                <div key={o.userId} className="outlier-card">
                  <div className="outlier-card-header">
                    <span className="outlier-name">{o.userName}</span>
                    <span className="outlier-badge">{o.multiplierVsAvg}× avg</span>
                  </div>
                  <div className="outlier-detail">
                    {o.scheduledHours.toFixed(1)}h total
                    {o.outsideHours > 0 && ` · ${o.outsideHours.toFixed(1)}h outside-hours`}
                    {` · ${o.totalInterruptions} interruptions`}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Team equity table */}
        <div className="fairness-team-table">
          <h4 className="fairness-section-title">
            Team equity breakdown
            <InfoIcon text="Equity Score per team = 100 − (team std deviation ÷ team mean × 100). Lower score = more uneven burden within that team." />
          </h4>
          <table className="comp-table">
            <thead>
              <tr>
                <th>Team</th>
                <th style={{ textAlign: "right" }}>Members</th>
                <th style={{ textAlign: "right" }}>Avg Hours</th>
                <th style={{ textAlign: "right" }}>
                  Std Dev
                  <InfoIcon text="Standard deviation of scheduled hours within this team." />
                </th>
                <th style={{ textAlign: "right" }}>
                  Outliers
                  <InfoIcon text={`Members carrying ≥ ${outlierMultiplier}× their team average.`} />
                </th>
                <th style={{ textAlign: "center" }}>Equity</th>
              </tr>
            </thead>
            <tbody>
              {data.teams.map((t) => (
                <tr key={t.teamId}>
                  <td>{t.teamName}</td>
                  <td className="num-cell">{t.memberCount}</td>
                  <td className="num-cell">{t.avgHours}h</td>
                  <td className="num-cell" style={{ color: t.stdDev > t.avgHours * 0.5 ? "var(--ooh-orange)" : undefined }}>{t.stdDev}h</td>
                  <td className="num-cell" style={{ color: t.outlierCount > 0 ? "var(--impacted-high)" : undefined }}>{t.outlierCount}</td>
                  <td style={{ textAlign: "center" }}>
                    <span className="equity-badge" style={{ color: equityColor(t.equityScore), background: "transparent", border: `1px solid ${equityColor(t.equityScore)}` }}>
                      {t.equityScore} / 100
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
