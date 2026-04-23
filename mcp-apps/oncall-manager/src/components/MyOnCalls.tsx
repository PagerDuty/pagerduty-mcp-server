import type { App } from "@modelcontextprotocol/ext-apps";
import { useState } from "react";
import type { CurrentUser, OnCallShift, Schedule } from "../api";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  currentUser: CurrentUser;
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  schedules: Schedule[];
  onOverrideCreated: () => void;
}

function isNow(shift: OnCallShift): boolean {
  const now = Date.now();
  return new Date(shift.start).getTime() <= now && new Date(shift.end).getTime() > now;
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString([], {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function countdownLabel(shift: OnCallShift): string {
  const ms = new Date(shift.start).getTime() - Date.now();
  if (ms <= 0) {
    const remaining = new Date(shift.end).getTime() - Date.now();
    const h = Math.floor(remaining / 3_600_000);
    const m = Math.floor((remaining % 3_600_000) / 60_000);
    return h > 0 ? `${h}h ${m}m remaining` : `${m}m remaining`;
  }
  const days = Math.floor(ms / 86_400_000);
  const h = Math.floor((ms % 86_400_000) / 3_600_000);
  return days > 0 ? `in ${days}d ${h}h` : `in ${h}h`;
}

function getDays(n = 7): Date[] {
  return Array.from({ length: n }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() + i);
    d.setHours(0, 0, 0, 0);
    return d;
  });
}

function shiftsOnDay(shifts: OnCallShift[], scheduleId: string, day: Date): OnCallShift[] {
  const start = day.getTime();
  const end = start + 86_400_000;
  return shifts.filter(
    (s) =>
      s.scheduleId === scheduleId &&
      new Date(s.start).getTime() < end &&
      new Date(s.end).getTime() > start,
  );
}

export function MyOnCalls({ app, currentUser, myShifts, allShifts, schedules, onOverrideCreated }: Props) {
  const [wizardShift, setWizardShift] = useState<OnCallShift | undefined>(undefined);
  const [showWizard, setShowWizard] = useState(false);

  const activeShift = myShifts.find(isNow);
  const upcomingShifts = myShifts.filter((s) => !isNow(s)).sort(
    (a, b) => new Date(a.start).getTime() - new Date(b.start).getTime(),
  );
  const nextShift = upcomingShifts[0];
  const days = getDays(7);

  const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div>
      {/* Countdown cards */}
      <p className="section-heading">My Shifts</p>
      <div className="countdown-row">
        {activeShift ? (
          <div className="countdown-card active-now">
            <div className="label">🟢 On-call now</div>
            <div className="schedule-name">{activeShift.scheduleName}</div>
            <div className="time-detail">
              {fmtDate(activeShift.start)} → {fmtDate(activeShift.end)}
            </div>
            <div className="time-detail" style={{ color: "var(--green)", fontWeight: 600 }}>
              {countdownLabel(activeShift)}
            </div>
            <div className="actions">
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => { setWizardShift(activeShift); setShowWizard(true); }}
              >
                🔄 Find coverage
              </button>
            </div>
          </div>
        ) : (
          <div className="countdown-card" style={{ borderColor: "var(--surface0)" }}>
            <div className="label" style={{ color: "var(--overlay0)" }}>Not on-call</div>
            <div className="schedule-name" style={{ color: "var(--overlay0)" }}>No active shift</div>
          </div>
        )}

        {nextShift ? (
          <div className="countdown-card upcoming">
            <div className="label">🔵 Next shift</div>
            <div className="schedule-name">{nextShift.scheduleName}</div>
            <div className="time-detail">
              {fmtDate(nextShift.start)} → {fmtDate(nextShift.end)}
            </div>
            <div className="time-detail" style={{ color: "var(--blue)", fontWeight: 600 }}>
              {countdownLabel(nextShift)}
            </div>
            <div className="actions">
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => { setWizardShift(nextShift); setShowWizard(true); }}
              >
                🔄 Find coverage
              </button>
            </div>
          </div>
        ) : (
          !activeShift && (
            <div className="countdown-card" style={{ borderColor: "var(--surface0)" }}>
              <div className="label" style={{ color: "var(--overlay0)" }}>Next shift</div>
              <div className="schedule-name" style={{ color: "var(--overlay0)" }}>No upcoming shifts</div>
            </div>
          )
        )}
      </div>

      {/* 7-day grid */}
      <p className="section-heading">7-Day Schedule</p>
      <div className="schedule-grid">
        <table className="grid-table">
          <thead>
            <tr>
              <th>Schedule</th>
              {days.map((d) => (
                <th key={d.toISOString()}>
                  <div>{DAY_NAMES[d.getDay()]}</div>
                  <div style={{ color: "var(--text)", fontWeight: 600 }}>{d.getDate()}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {schedules.map((sched) => (
              <tr key={sched.id}>
                <td>{sched.name}</td>
                {days.map((day) => {
                  const dayShifts = shiftsOnDay(allShifts, sched.id, day);
                  if (dayShifts.length === 0) {
                    return <td key={day.toISOString()} />;
                  }
                  return (
                    <td key={day.toISOString()}>
                      {dayShifts.map((s, i) => {
                        const isMine = s.scheduleId === sched.id &&
                          myShifts.some((ms) => ms.scheduleId === s.scheduleId && ms.start === s.start);
                        return (
                          <span key={i} className={`shift-block ${isMine ? "mine" : "other"}`}>
                            {isMine ? currentUser.name.split(" ")[0] : "●"}
                          </span>
                        );
                      })}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Coverage wizard */}
      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          preselectedShift={wizardShift}
          onClose={() => setShowWizard(false)}
          onDone={() => { setShowWizard(false); onOverrideCreated(); }}
        />
      )}
    </div>
  );
}
