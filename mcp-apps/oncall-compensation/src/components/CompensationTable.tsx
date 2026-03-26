import type { UserCompensationRecord } from "../api";

export type SortKey =
  | "userName"
  | "scheduledHours"
  | "incidentCount"
  | "highUrgencyCount"
  | "incidentHours"
  | "interruptionRate"
  | "offHourInterruptions"
  | "sleepHourInterruptions"
  | "businessHourInterruptions"
  | "outsideHours"
  | "weekendHours"
  | "holidayHours"
  | "maxConsecutiveOutsideHours"
  | "uniquePeriodsOutside";

interface Props {
  records: UserCompensationRecord[];
  selectedId: string | null;
  onSelect: (userId: string) => void;
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
  visibleCols: Set<SortKey>;
}

export interface ColDef {
  key: SortKey;
  label: string;
  align?: "right";
  toggleable: boolean;
  group?: "bh"; // business-hours group gets a subtle visual distinction
}

export const ALL_COLS: ColDef[] = [
  { key: "userName",                    label: "User",              toggleable: false },
  { key: "scheduledHours",              label: "Oncall Hrs",        align: "right", toggleable: true },
  { key: "incidentCount",               label: "Incidents",         align: "right", toggleable: true },
  { key: "highUrgencyCount",            label: "High Urgency",      align: "right", toggleable: true },
  { key: "incidentHours",               label: "Response Hrs",      align: "right", toggleable: true },
  { key: "interruptionRate",            label: "Rate /hr",          align: "right", toggleable: true },
  { key: "offHourInterruptions",        label: "Off-Hr Intrs",      align: "right", toggleable: true },
  { key: "sleepHourInterruptions",      label: "Sleep Intrs",       align: "right", toggleable: true },
  { key: "businessHourInterruptions",   label: "BH Intrs",          align: "right", toggleable: true },
  // Business-hours config derived columns
  { key: "outsideHours",                label: "Outside BH Hrs",    align: "right", toggleable: true, group: "bh" },
  { key: "weekendHours",                label: "Weekend Hrs",       align: "right", toggleable: true, group: "bh" },
  { key: "holidayHours",                label: "Holiday Hrs",       align: "right", toggleable: true, group: "bh" },
  { key: "maxConsecutiveOutsideHours",  label: "Max Consec. Hrs",   align: "right", toggleable: true, group: "bh" },
  { key: "uniquePeriodsOutside",        label: "Unique Periods",    align: "right", toggleable: true, group: "bh" },
];

const HIGH_RATE_THRESHOLD = 0.5;

function fmtHours(h: number): string {
  return h > 0 ? `${h.toFixed(1)}h` : "—";
}

function renderCell(r: UserCompensationRecord, key: SortKey) {
  switch (key) {
    case "userName":
      return (
        <td key={key}>
          <div className="user-cell">
            <span className="user-name">{r.userName}</span>
            {r.teamName && (() => {
              const teams = r.teamName.split(", ");
              const label = teams.length > 1
                ? `${teams[0]}  +${teams.length - 1} more`
                : teams[0];
              return <span className="user-team" title={r.teamName}>{label}</span>;
            })()}
          </div>
        </td>
      );
    case "scheduledHours":
      return <td key={key} className="num-cell">{r.scheduledHours.toFixed(1)}h</td>;
    case "incidentCount":
      return <td key={key} className="num-cell">{r.incidentCount}</td>;
    case "highUrgencyCount":
      return (
        <td key={key} className="num-cell">
          {r.highUrgencyCount > 0 ? (
            <span className="urgency-chip high">{r.highUrgencyCount} high</span>
          ) : (
            <span style={{ color: "var(--text-muted)" }}>—</span>
          )}
        </td>
      );
    case "incidentHours":
      return <td key={key} className="num-cell">{r.incidentHours.toFixed(1)}h</td>;
    case "interruptionRate":
      return (
        <td
          key={key}
          className={[
            "num-cell",
            "rate-cell",
            r.interruptionRate >= HIGH_RATE_THRESHOLD ? "high-rate" : "",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          {r.interruptionRate.toFixed(3)}
        </td>
      );
    case "offHourInterruptions":
      return (
        <td
          key={key}
          className={["num-cell", "ooh-cell", r.offHourInterruptions > 0 ? "ooh-high" : ""]
            .filter(Boolean)
            .join(" ")}
        >
          {r.offHourInterruptions > 0 ? r.offHourInterruptions : <span style={{ color: "var(--text-muted)" }}>—</span>}
        </td>
      );
    case "sleepHourInterruptions":
      return (
        <td key={key} className="num-cell ooh-cell">
          {r.sleepHourInterruptions > 0 ? r.sleepHourInterruptions : <span style={{ color: "var(--text-muted)" }}>—</span>}
        </td>
      );
    case "businessHourInterruptions":
      return (
        <td key={key} className="num-cell">
          {r.businessHourInterruptions > 0 ? r.businessHourInterruptions : <span style={{ color: "var(--text-muted)" }}>—</span>}
        </td>
      );
    case "outsideHours":
      return (
        <td key={key} className={["num-cell", "bh-cell", r.outsideHours > 0 ? "bh-cell--high" : ""].filter(Boolean).join(" ")}>
          {fmtHours(r.outsideHours)}
        </td>
      );
    case "weekendHours":
      return (
        <td key={key} className="num-cell bh-cell">
          {fmtHours(r.weekendHours)}
        </td>
      );
    case "holidayHours":
      return (
        <td key={key} className="num-cell bh-cell">
          {fmtHours(r.holidayHours)}
        </td>
      );
    case "maxConsecutiveOutsideHours":
      return (
        <td key={key} className="num-cell bh-cell">
          {fmtHours(r.maxConsecutiveOutsideHours)}
        </td>
      );
    case "uniquePeriodsOutside":
      return (
        <td key={key} className="num-cell bh-cell">
          {r.uniquePeriodsOutside > 0 ? r.uniquePeriodsOutside : <span style={{ color: "var(--text-muted)" }}>—</span>}
        </td>
      );
  }
}

export function CompensationTable({
  records,
  selectedId,
  onSelect,
  sortKey,
  sortDir,
  onSort,
  visibleCols,
}: Props) {
  const cols = ALL_COLS.filter((c) => !c.toggleable || visibleCols.has(c.key));

  if (records.length === 0) {
    return (
      <div className="table-empty">
        No oncall data found for the selected period.
      </div>
    );
  }

  return (
    <table className="comp-table">
      <thead>
        <tr>
          {cols.map((col) => (
            <th
              key={col.key}
              className={[
                col.toggleable ? "sortable" : "",
                sortKey === col.key ? "sort-active" : "",
                col.group === "bh" ? "th-bh" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              style={col.align ? { textAlign: col.align } : undefined}
              onClick={() => col.toggleable && onSort(col.key)}
            >
              {col.label}
              {sortKey === col.key && (
                <span className="sort-arrow">
                  {sortDir === "desc" ? "↓" : "↑"}
                </span>
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {records.map((r) => (
          <tr
            key={r.userId}
            className={selectedId === r.userId ? "selected" : ""}
            onClick={() => onSelect(r.userId)}
          >
            {cols.map((col) => renderCell(r, col.key))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
