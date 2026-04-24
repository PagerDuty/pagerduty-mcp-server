import type { ResponderMetric } from "../api";
import { fmtMin } from "../utils";

interface CompensationPageProps {
  metrics: ResponderMetric[];
}

function fmtHours(h: number): string {
  return `${h}h`;
}

export function CompensationPage({ metrics }: CompensationPageProps) {
  if (metrics.length === 0) {
    return <div className="comp-empty">No responder data available for this period.</div>;
  }

  const totalOnCallHours = metrics.reduce((s, r) => s + r.onCallHours, 0);
  const avgOnCallHours = metrics.length > 0
    ? Math.round((totalOnCallHours / metrics.length) * 10) / 10
    : 0;
  const totalSleepInt = metrics.reduce((s, r) => s + r.sleepInterruptions, 0);
  const highRiskCount = metrics.filter((r) => r.riskLevel === "high").length;

  const sorted = [...metrics].sort((a, b) => b.onCallHours - a.onCallHours);

  return (
    <div className="comp-page">
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

      <div className="analytics-section">
        <div className="section-title">
          Responder On-Call Summary
          <span className="section-count">{metrics.length}</span>
        </div>
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Responder</th>
              <th className="col-num">On-Call Hrs</th>
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
