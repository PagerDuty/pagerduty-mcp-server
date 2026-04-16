import type { OpsData } from "../api";

function fmtMttr(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

interface CardProps {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}

function Card({ label, value, sub, accent }: CardProps) {
  return (
    <div className="summary-card">
      <div className="summary-label">{label}</div>
      <div className="summary-value" style={accent ? { color: accent } : undefined}>{value}</div>
      {sub && <div className="summary-sub">{sub}</div>}
    </div>
  );
}

export function SummaryCards({ data }: { data: OpsData }) {
  const highPct = data.totalIncidents > 0
    ? Math.round((data.highUrgencyCount / data.totalIncidents) * 100)
    : 0;

  return (
    <div className="summary-cards">
      <Card
        label="Total Incidents"
        value={String(data.totalIncidents)}
        sub={`${data.resolvedCount} resolved`}
      />
      <Card
        label="High Urgency"
        value={String(data.highUrgencyCount)}
        sub={`${highPct}% of total`}
        accent={data.highUrgencyCount > 0 ? "var(--status-triggered)" : undefined}
      />
      <Card
        label="Avg MTTR"
        value={fmtMttr(data.mttrMinutes)}
        sub="mean time to resolve"
        accent={
          data.mttrMinutes !== null && data.mttrMinutes > 60
            ? "var(--color-escalation)"
            : undefined
        }
      />
      <Card
        label="On-Call Users"
        value={String(data.oncallUsers.length)}
        sub={data.oncallUsers.slice(0, 2).join(", ") || "—"}
      />
    </div>
  );
}
