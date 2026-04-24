import { useState } from "react";
import type { ResponderMetric, TeamMetric } from "../api";
import { fmtMin } from "../utils";

type SortKey = "sleepInterruptions" | "offHourInterruptions" | "businessHourInterruptions" | "onCallHours" | "engagedMinutes" | "totalIncidents";

interface TeamHealthProps {
  metrics: ResponderMetric[];
  teamMetrics: TeamMetric[];
}

function RiskBadge({ level }: { level: "high" | "medium" | "low" }) {
  const labels = { high: "High", medium: "Medium", low: "Low" };
  return <span className={`risk-badge risk-${level}`}>{labels[level]}</span>;
}

export function TeamHealth({ metrics, teamMetrics }: TeamHealthProps) {
  const [sortKey, setSortKey] = useState<SortKey>("sleepInterruptions");
  const [selectedTeam, setSelectedTeam] = useState<string>("");

  const teamNames = Array.from(new Set(metrics.map((r) => r.teamName).filter(Boolean))) as string[];
  const filtered = selectedTeam ? metrics.filter((r) => r.teamName === selectedTeam) : metrics;

  const highCount = filtered.filter((r) => r.riskLevel === "high").length;
  const medCount = filtered.filter((r) => r.riskLevel === "medium").length;
  const lowCount = filtered.filter((r) => r.riskLevel === "low").length;
  const totalSleepInt = filtered.reduce((s, r) => s + r.sleepInterruptions, 0);

  const sorted = [...filtered].sort((a, b) => {
    if (sortKey === "engagedMinutes") {
      return (b.engagedMinutes ?? 0) - (a.engagedMinutes ?? 0);
    }
    return (b[sortKey] as number) - (a[sortKey] as number);
  });

  const sortedTeams = [...teamMetrics].sort(
    (a, b) => (b.businessHourInterruptions + b.offHourInterruptions + b.sleepHourInterruptions) -
               (a.businessHourInterruptions + a.offHourInterruptions + a.sleepHourInterruptions)
  );

  function ThSort({ col, label }: { col: SortKey; label: string }) {
    return (
      <th
        className={`col-num th-sortable${sortKey === col ? " th-active" : ""}`}
        onClick={() => setSortKey(col)}
      >
        {label}{sortKey === col ? " ↓" : ""}
      </th>
    );
  }

  return (
    <div className="body">
      {/* Team filter */}
      {teamNames.length > 0 && (
        <div className="th-filter-bar">
          <select
            className="ctrl-btn"
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.currentTarget.value)}
          >
            <option value="">All teams</option>
            {teamNames.sort().map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      )}

      {/* Fatigue risk summary */}
      <div className="fatigue-summary">
        <div className="fatigue-kpi-card fatigue-high">
          <div className="kpi-label">High Risk</div>
          <div className="kpi-value">{highCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
        <div className="fatigue-kpi-card fatigue-medium">
          <div className="kpi-label">Medium Risk</div>
          <div className="kpi-value">{medCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
        <div className="fatigue-kpi-card fatigue-low">
          <div className="kpi-label">Low Risk</div>
          <div className="kpi-value">{lowCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
        <div className="fatigue-kpi-card">
          <div className="kpi-label">Sleep Interruptions</div>
          <div className="kpi-value">{totalSleepInt}</div>
          <div className="kpi-sub">total this period</div>
        </div>
      </div>

      {/* Responder burden table */}
      <div className="analytics-section">
        <div className="section-title">Responder Burden</div>
        {metrics.length === 0 ? (
          <div className="empty-state">No responder data for this period</div>
        ) : (
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Responder</th>
                <ThSort col="onCallHours"              label="On-Call Hrs" />
                <ThSort col="sleepInterruptions"       label="Sleep Int" />
                <ThSort col="offHourInterruptions"     label="Off-Hr Int" />
                <ThSort col="businessHourInterruptions" label="Business Int" />
                <ThSort col="engagedMinutes"           label="Engaged Time" />
                <ThSort col="totalIncidents"           label="Incidents" />
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
                  <td className="col-num col-mono">{r.onCallHours}h</td>
                  <td className={`col-num${r.sleepInterruptions >= 5 ? " col-warn" : r.sleepInterruptions >= 2 ? "" : " col-ok"}`}>
                    {r.sleepInterruptions}
                  </td>
                  <td className="col-num">{r.offHourInterruptions}</td>
                  <td className="col-num">{r.businessHourInterruptions}</td>
                  <td className="col-num col-mono">{fmtMin(r.engagedMinutes)}</td>
                  <td className="col-num">{r.totalIncidents}</td>
                  <td className="col-num"><RiskBadge level={r.riskLevel} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Team interruption breakdown */}
      <div className="analytics-section">
        <div className="section-title">Team Interruption Breakdown</div>
        {teamMetrics.length === 0 ? (
          <div className="empty-state">No team data for this period</div>
        ) : (
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Team</th>
                <th className="col-num">Business Hrs</th>
                <th className="col-num">Off Hrs</th>
                <th className="col-num">Sleep Hrs</th>
                <th className="col-num">Total Int</th>
                <th className="col-num">Mean Engaged</th>
              </tr>
            </thead>
            <tbody>
              {sortedTeams.map((t) => (
                <tr key={t.id}>
                  <td className="col-name">{t.name}</td>
                  <td className="col-num">{t.businessHourInterruptions}</td>
                  <td className="col-num">{t.offHourInterruptions}</td>
                  <td className={`col-num${t.sleepHourInterruptions > 0 ? " col-warn" : " col-ok"}`}>
                    {t.sleepHourInterruptions}
                  </td>
                  <td className="col-num">{t.totalInterruptions}</td>
                  <td className="col-num col-mono">{fmtMin(t.meanEngagedMinutes)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
