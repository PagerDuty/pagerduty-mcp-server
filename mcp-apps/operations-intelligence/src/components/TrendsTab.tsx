import type { TrendsData, TrendPoint } from "../api";

interface TrendsTabProps {
  trendsData: TrendsData | null;
}

const CHART_W = 600;
const CHART_H = 120;
const PAD = { top: 10, right: 16, bottom: 28, left: 44 };

function plotW() { return CHART_W - PAD.left - PAD.right; }
function plotH() { return CHART_H - PAD.top - PAD.bottom; }

function formatWeek(weekStart: string): string {
  const d = new Date(weekStart + "T00:00:00");
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

interface BarChartProps {
  points: TrendPoint[];
  getValue: (p: TrendPoint) => number;
  color: string;
  yLabel: string;
}

function BarChart({ points, getValue, color, yLabel }: BarChartProps) {
  if (points.length === 0) return <div className="chart-empty">No data</div>;
  const values = points.map(getValue);
  const maxVal = Math.max(...values, 1);
  const barW = plotW() / points.length * 0.6;
  const barGap = plotW() / points.length;

  return (
    <svg
      viewBox={`0 0 ${CHART_W} ${CHART_H}`}
      className="trend-chart"
      preserveAspectRatio="xMidYMid meet"
    >
      <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + plotH()} stroke="var(--border-2)" strokeWidth="1" />
      <text x={8} y={PAD.top + plotH() / 2} fontSize="10" fill="var(--text-2)" textAnchor="middle" transform={`rotate(-90, 8, ${PAD.top + plotH() / 2})`}>{yLabel}</text>
      <text x={PAD.left - 4} y={PAD.top + plotH()} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">0</text>
      <text x={PAD.left - 4} y={PAD.top} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">{maxVal}</text>
      {points.map((p, i) => {
        const val = getValue(p);
        const barH = (val / maxVal) * plotH();
        const x = PAD.left + i * barGap + (barGap - barW) / 2;
        const y = PAD.top + plotH() - barH;
        return (
          <g key={p.weekStart}>
            <rect x={x} y={y} width={barW} height={barH} fill={color} rx="2" opacity="0.85" />
            <text x={x + barW / 2} y={PAD.top + plotH() + 14} fontSize="9" fill="var(--text-2)" textAnchor="middle">{formatWeek(p.weekStart)}</text>
          </g>
        );
      })}
    </svg>
  );
}

interface LineChartProps {
  points: TrendPoint[];
  getValue: (p: TrendPoint) => number | null;
  color: string;
  yLabel: string;
}

function LineChart({ points, getValue, color, yLabel }: LineChartProps) {
  const valid = points.filter((p) => getValue(p) !== null);
  if (valid.length === 0) return <div className="chart-empty">No data</div>;
  const values = valid.map((p) => getValue(p) as number);
  const maxVal = Math.max(...values, 1);
  const minVal = Math.min(...values, 0);
  const range = maxVal - minVal || 1;

  function xOf(i: number) {
    return PAD.left + (i / (points.length - 1 || 1)) * plotW();
  }
  function yOf(val: number) {
    return PAD.top + plotH() - ((val - minVal) / range) * plotH();
  }

  const polyPoints = points
    .map((p, i) => {
      const v = getValue(p);
      return v !== null ? `${xOf(i)},${yOf(v)}` : null;
    })
    .filter(Boolean)
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${CHART_W} ${CHART_H}`}
      className="trend-chart"
      preserveAspectRatio="xMidYMid meet"
    >
      <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + plotH()} stroke="var(--border-2)" strokeWidth="1" />
      <text x={8} y={PAD.top + plotH() / 2} fontSize="10" fill="var(--text-2)" textAnchor="middle" transform={`rotate(-90, 8, ${PAD.top + plotH() / 2})`}>{yLabel}</text>
      <text x={PAD.left - 4} y={PAD.top + plotH()} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">{minVal}</text>
      <text x={PAD.left - 4} y={PAD.top} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">{maxVal}</text>
      <polyline points={polyPoints} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {points.map((p, i) => {
        const v = getValue(p);
        return (
          <g key={p.weekStart}>
            {v !== null && (
              <circle cx={xOf(i)} cy={yOf(v)} r="3.5" fill={color} />
            )}
            <text x={xOf(i)} y={PAD.top + plotH() + 14} fontSize="9" fill="var(--text-2)" textAnchor="middle">{formatWeek(p.weekStart)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function TrendsTab({ trendsData }: TrendsTabProps) {
  if (!trendsData || trendsData.points.length === 0) {
    return <div className="trends-empty">No trend data available for this period.</div>;
  }

  return (
    <div className="trends-tab">
      <div className="trend-card">
        <div className="trend-card-title">Incident Volume (per week)</div>
        <BarChart points={trendsData.points} getValue={(p) => p.totalIncidents} color="var(--red)" yLabel="Incidents" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">MTTA — Mean Time to Ack (minutes)</div>
        <LineChart points={trendsData.points} getValue={(p) => p.mttaMinutes} color="var(--blue)" yLabel="min" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">MTTR — Mean Time to Resolve (minutes)</div>
        <LineChart points={trendsData.points} getValue={(p) => p.mttrMinutes} color="var(--green)" yLabel="min" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">Interruptions (per week)</div>
        <BarChart points={trendsData.points} getValue={(p) => p.totalInterruptions} color="var(--amber)" yLabel="Count" />
      </div>
    </div>
  );
}
