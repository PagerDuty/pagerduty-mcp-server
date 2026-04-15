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
  description: string;
  align?: "right";
  toggleable: boolean;
  group?: "bh"; // business-hours group gets a subtle visual distinction
}

export const ALL_COLS: ColDef[] = [
  { key: "userName",                    label: "User",              description: "User name and their team memberships.",                                                                                          toggleable: false },
  { key: "scheduledHours",              label: "Oncall Hrs",        description: "Total hours scheduled on-call during the selected period, from PagerDuty Analytics.",                                           align: "right", toggleable: true },
  { key: "incidentCount",               label: "Incidents",         description: "Total number of incidents this user was involved in during the period.",                                                         align: "right", toggleable: true },
  { key: "highUrgencyCount",            label: "High Urgency",      description: "Number of high-urgency incidents assigned to this user.",                                                                        align: "right", toggleable: true },
  { key: "incidentHours",               label: "Response Hrs",      description: "Total time engaged in incident response — from incident creation to resolution, capped at 24h per incident.",                   align: "right", toggleable: true },
  { key: "interruptionRate",            label: "Rate /hr",          description: "Interruptions per on-call hour (total interruptions ÷ scheduled hours). Higher values indicate more frequent paging.",           align: "right", toggleable: true },
  { key: "offHourInterruptions",        label: "Off-Hr Intrs",      description: "Interruptions that occurred outside of business hours, as defined by PagerDuty Analytics (evenings and early mornings).",       align: "right", toggleable: true },
  { key: "sleepHourInterruptions",      label: "Sleep Intrs",       description: "Interruptions during typical sleep hours (roughly 10pm–8am), from PagerDuty Analytics.",                                        align: "right", toggleable: true },
  { key: "businessHourInterruptions",   label: "BH Intrs",          description: "Interruptions that occurred during standard business hours, from PagerDuty Analytics.",                                          align: "right", toggleable: true },
  // Business-hours config derived columns
  { key: "outsideHours",                label: "Outside BH Hrs",    description: "Total on-call hours outside your configured business hours (days + time window). Computed from raw shift windows + BH config.",  align: "right", toggleable: true, group: "bh" },
  { key: "weekendHours",                label: "Weekend Hrs",        description: "On-call hours that fell on weekend days, based on your configured work days.",                                                   align: "right", toggleable: true, group: "bh" },
  { key: "holidayHours",                label: "Holiday Hrs",        description: "On-call hours that fell on configured holidays.",                                                                                align: "right", toggleable: true, group: "bh" },
  { key: "maxConsecutiveOutsideHours",  label: "Max Consec. Hrs",   description: "Longest single unbroken stretch of on-call time outside business hours. Useful for identifying sustained out-of-hours burden.",  align: "right", toggleable: true, group: "bh" },
  { key: "uniquePeriodsOutside",        label: "Unique Periods",    description: "Number of distinct separate windows where this user was on-call outside business hours. High count = frequently interrupted.",    align: "right", toggleable: true, group: "bh" },
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
              <span className="col-info" onClick={(e) => e.stopPropagation()}>
                ⓘ
                <span className="col-tooltip">{col.description}</span>
              </span>
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
