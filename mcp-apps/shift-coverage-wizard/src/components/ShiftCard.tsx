import type { OnCallShift } from "../api";

interface ShiftCardProps {
  shift: OnCallShift;
  selected: boolean;
  onSelect: () => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function durationHours(start: string, end: string): string {
  const h = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 3_600_000);
  return h >= 24 ? `${Math.round(h / 24)}d` : `${h}h`;
}

export function ShiftCard({ shift, selected, onSelect }: ShiftCardProps) {
  return (
    <div
      className={`shift-card ${selected ? "selected" : ""}`}
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => e.key === "Enter" && onSelect()}
      aria-pressed={selected}
    >
      <div className="shift-card-radio">{selected ? "◉" : "○"}</div>
      <div className="shift-card-body">
        <div className="shift-card-name">{shift.scheduleName}</div>
        <div className="shift-card-range">
          {fmt(shift.start)} → {fmt(shift.end)}{" "}
          <span className="shift-card-duration">({durationHours(shift.start, shift.end)})</span>
        </div>
        {shift.escalationLevel > 0 && (
          <div className="shift-card-level">Escalation level {shift.escalationLevel}</div>
        )}
      </div>
    </div>
  );
}
