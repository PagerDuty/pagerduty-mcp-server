import type { UserCompensationRecord } from "../api";

interface Props {
  records: UserCompensationRecord[];
}

export function SummaryCards({ records }: Props) {
  const totalUsers = records.length;
  const totalOncallHours = records.reduce((s, r) => s + r.scheduledHours, 0);
  const totalIncidents = records.reduce((s, r) => s + r.incidentCount, 0);
  const avgIncidents = totalUsers > 0 ? totalIncidents / totalUsers : 0;
  const totalOffHourIntrs = records.reduce((s, r) => s + r.offHourInterruptions, 0);
  const totalSleepIntrs = records.reduce((s, r) => s + r.sleepHourInterruptions, 0);

  const totalOutsideHours = records.reduce((s, r) => s + r.outsideHours, 0);
  const totalWeekendHours = records.reduce((s, r) => s + r.weekendHours, 0);
  const totalHolidayHours = records.reduce((s, r) => s + r.holidayHours, 0);
  const hasOutsideData = totalOutsideHours > 0;

  return (
    <div className="summary-cards">
      <div className="summary-card">
        <div className="card-value">{totalUsers}</div>
        <div className="card-label">Users On-Call</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{totalOncallHours.toFixed(0)}h</div>
        <div className="card-label">Total Oncall Hours</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{totalIncidents}</div>
        <div className="card-label">Incidents Responded</div>
        <div className="card-sub">
          {records.reduce((s, r) => s + r.highUrgencyCount, 0)} high ·{" "}
          {records.reduce((s, r) => s + r.lowUrgencyCount, 0)} low
        </div>
      </div>
      <div className="summary-card">
        <div className="card-value">{avgIncidents.toFixed(1)}</div>
        <div className="card-label">Avg Incidents / User</div>
      </div>
      {(totalOffHourIntrs > 0 || totalSleepIntrs > 0) && (
        <div className="summary-card">
          <div className="card-value ooh-value">{totalOffHourIntrs + totalSleepIntrs}</div>
          <div className="card-label">OOH Interruptions</div>
          <div className="card-sub">
            {totalOffHourIntrs} off-hr · {totalSleepIntrs} sleep
          </div>
        </div>
      )}
      {hasOutsideData && (
        <div className="summary-card summary-card--bh">
          <div className="card-value bh-value">{totalOutsideHours.toFixed(1)}h</div>
          <div className="card-label">Outside BH Hours</div>
          <div className="card-sub">
            {totalWeekendHours.toFixed(1)}h wknd
            {totalHolidayHours > 0 ? ` · ${totalHolidayHours.toFixed(1)}h holiday` : ""}
          </div>
        </div>
      )}
    </div>
  );
}
