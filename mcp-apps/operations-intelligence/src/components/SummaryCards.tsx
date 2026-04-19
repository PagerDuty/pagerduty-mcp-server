import type { OpsData } from "../api";
import { fmtMin } from "../utils";

interface KpiCardProps {
  label: string;
  value: string;
  sub?: string;
  warn?: boolean;
}

function KpiCard({ label, value, sub, warn }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={warn ? { color: "var(--color-escalation)" } : undefined}>
        {value}
      </div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export function SummaryCards({ data }: { data: OpsData }) {
  return (
    <div className="kpi-bar">
      <KpiCard
        label="Total Incidents"
        value={String(data.totalIncidents)}
        sub={`${data.teamMetrics.length} team${data.teamMetrics.length !== 1 ? "s" : ""}`}
      />
      <KpiCard
        label="MTTA"
        value={fmtMin(data.mttaMinutes)}
        sub="mean time to ack"
        warn={data.mttaMinutes !== null && data.mttaMinutes > 30}
      />
      <KpiCard
        label="MTTR"
        value={fmtMin(data.mttrMinutes)}
        sub="mean time to resolve"
        warn={data.mttrMinutes !== null && data.mttrMinutes > 60}
      />
      <KpiCard
        label="Escalation Rate"
        value={data.escalationRate !== null ? `${data.escalationRate}%` : "—"}
        sub="of all incidents"
        warn={data.escalationRate !== null && data.escalationRate > 20}
      />
      <KpiCard
        label="Avg Uptime"
        value={data.uptimePct !== null ? `${data.uptimePct}%` : "—"}
        sub="across services"
        warn={data.uptimePct !== null && data.uptimePct < 99}
      />
    </div>
  );
}
