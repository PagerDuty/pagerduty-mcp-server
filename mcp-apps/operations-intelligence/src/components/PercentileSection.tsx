import { useState } from "react";
import type { AggregatedMetrics } from "../api";

function fmtSec(seconds: number | null): string {
  if (seconds === null) return "—";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

interface PercentileCellProps {
  label: string;
  value: number | null;
}

function PercentileCell({ label, value }: PercentileCellProps) {
  return (
    <div className="percentile-cell">
      <div className="percentile-label">{label}</div>
      <div className="percentile-value">{fmtSec(value)}</div>
    </div>
  );
}

interface PercentileSectionProps {
  aggregated: AggregatedMetrics | null;
}

export function PercentileSection({ aggregated }: PercentileSectionProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="percentile-section">
      <button className="percentile-toggle" onClick={() => setOpen((o) => !o)}>
        <span>{open ? "▼" : "▶"}</span>
        Percentile Distribution
      </button>
      {open && (
        <div className="percentile-grid">
          <PercentileCell label="P50 Ack"     value={aggregated?.p50AckSeconds ?? null} />
          <PercentileCell label="P75 Ack"     value={aggregated?.p75AckSeconds ?? null} />
          <PercentileCell label="P90 Ack"     value={aggregated?.p90AckSeconds ?? null} />
          <PercentileCell label="P95 Ack"     value={aggregated?.p95AckSeconds ?? null} />
          <PercentileCell label="P50 Resolve" value={aggregated?.p50ResolveSeconds ?? null} />
          <PercentileCell label="P75 Resolve" value={aggregated?.p75ResolveSeconds ?? null} />
          <PercentileCell label="P90 Resolve" value={aggregated?.p90ResolveSeconds ?? null} />
          <PercentileCell label="P95 Resolve" value={aggregated?.p95ResolveSeconds ?? null} />
        </div>
      )}
    </div>
  );
}
