import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, fetchScheduleUsers } from "../api";
import type { OnCallShift, Override, Schedule, ScheduleUser } from "../api";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  schedules: Schedule[];
  overrides: Override[];
  myShifts: OnCallShift[];
  onOverrideCreated: () => void;
}

function fmtRange(start: string, end: string): string {
  const fmt = (iso: string) =>
    new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  return `${fmt(start)} → ${fmt(end)}`;
}

function toLocalInput(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function fromLocalInput(local: string): string {
  return new Date(local).toISOString();
}

export function OverridesTab({ app, schedules, overrides, myShifts, onOverrideCreated }: Props) {
  const [showForm, setShowForm] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const [formSchedule, setFormSchedule] = useState(schedules[0]?.id ?? "");
  const [formUsers, setFormUsers] = useState<ScheduleUser[]>([]);
  const [formUser, setFormUser] = useState("");
  const [formStart, setFormStart] = useState(toLocalInput(new Date().toISOString()));
  const [formEnd, setFormEnd] = useState(toLocalInput(new Date(Date.now() + 86_400_000).toISOString()));
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!formSchedule) return;
    fetchScheduleUsers(app, formSchedule)
      .then((users) => {
        setFormUsers(users);
        setFormUser(users[0]?.id ?? "");
      })
      .catch(() => setFormUsers([]));
  }, [formSchedule]);

  async function handleCreate() {
    if (!formSchedule || !formUser) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const ok = await createOverride(
        app,
        formSchedule,
        formUser,
        fromLocalInput(formStart),
        fromLocalInput(formEnd),
      );
      if (ok) {
        setShowForm(false);
        onOverrideCreated();
      } else {
        setFormError("Failed to create override.");
      }
    } catch (e: any) {
      setFormError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  const upcoming = overrides
    .filter((o) => new Date(o.end).getTime() > Date.now())
    .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <p className="section-heading" style={{ marginBottom: 0 }}>Active & Upcoming Overrides</p>
        <div style={{ display: "flex", gap: 6 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => { setShowWizard(true); }}>
            🔄 Find Coverage
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm((v) => !v)}>
            {showForm ? "Cancel" : "+ New Override"}
          </button>
        </div>
      </div>

      {/* Inline create form */}
      {showForm && (
        <div className="create-override-form" style={{ marginBottom: 16 }}>
          {formError && <p className="error-banner">{formError}</p>}
          <div className="form-row">
            <div className="form-field">
              <label>Schedule</label>
              <select value={formSchedule} onChange={(e) => setFormSchedule((e.target as HTMLSelectElement).value)}>
                {schedules.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>Override user</label>
              <select value={formUser} onChange={(e) => setFormUser((e.target as HTMLSelectElement).value)}>
                {formUsers.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-field">
              <label>Start</label>
              <input
                type="datetime-local"
                value={formStart}
                onChange={(e) => setFormStart((e.target as HTMLInputElement).value)}
              />
            </div>
            <div className="form-field">
              <label>End</label>
              <input
                type="datetime-local"
                value={formEnd}
                onChange={(e) => setFormEnd((e.target as HTMLInputElement).value)}
              />
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="btn btn-primary" onClick={handleCreate} disabled={submitting || !formSchedule || !formUser}>
              {submitting ? "Creating…" : "Create Override"}
            </button>
          </div>
        </div>
      )}

      {/* Override list */}
      <div className="override-list">
        {upcoming.length === 0 && (
          <p className="empty-state">No active or upcoming overrides.</p>
        )}
        {upcoming.map((o) => (
          <div key={o.id} className="override-row">
            <div>
              <div className="or-schedule">{o.scheduleName}</div>
              <div className="or-user">{o.userName}</div>
              <div className="or-dates">{fmtRange(o.start, o.end)}</div>
            </div>
            <div className="or-actions">
              <span
                style={{ fontSize: 10, padding: "2px 7px", borderRadius: 3, background: "var(--surface0)", color: "var(--subtext0)" }}
              >
                {new Date(o.start).getTime() <= Date.now() ? "Active" : "Upcoming"}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Coverage wizard */}
      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          onClose={() => setShowWizard(false)}
          onDone={() => { setShowWizard(false); onOverrideCreated(); }}
        />
      )}
    </div>
  );
}
