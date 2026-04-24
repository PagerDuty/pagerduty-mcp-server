import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, deleteOverride, fetchScheduleOverrides, fetchScheduleUsers } from "../api";
import type { OnCallShift, OverrideDetail, Schedule, ScheduleUser } from "../api";
import { USER_COLOR_FG, userColor } from "../utils/userColor";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  schedules: Schedule[];
  myShifts: OnCallShift[];
  onClose: () => void;
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

export function OverridesModal({ app, schedules, myShifts, onClose }: Props) {
  const [selectedScheduleId, setSelectedScheduleId] = useState(schedules[0]?.id ?? "");
  const [overrides, setOverrides] = useState<OverrideDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  const [formUsers, setFormUsers] = useState<ScheduleUser[]>([]);
  const [formUser, setFormUser] = useState("");
  const [formStart, setFormStart] = useState(toLocalInput(new Date().toISOString()));
  const [formEnd, setFormEnd] = useState(toLocalInput(new Date(Date.now() + 86_400_000).toISOString()));
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const since = new Date().toISOString();
  const until = new Date(Date.now() + 30 * 86_400_000).toISOString();

  useEffect(() => {
    if (!selectedScheduleId) return;
    setLoading(true);
    fetchScheduleOverrides(app, selectedScheduleId, since, until)
      .then((items) => {
        const sched = schedules.find((s) => s.id === selectedScheduleId);
        setOverrides(items.map((o) => ({ ...o, scheduleName: sched?.name ?? selectedScheduleId })));
      })
      .catch(() => setOverrides([]))
      .finally(() => setLoading(false));
  }, [selectedScheduleId]);

  useEffect(() => {
    if (!selectedScheduleId) return;
    fetchScheduleUsers(app, selectedScheduleId)
      .then((users) => {
        setFormUsers(users);
        setFormUser(users[0]?.id ?? "");
      })
      .catch(() => setFormUsers([]));
  }, [selectedScheduleId]);

  async function handleCreate() {
    if (!selectedScheduleId || !formUser) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const ok = await createOverride(app, selectedScheduleId, formUser, new Date(formStart).toISOString(), new Date(formEnd).toISOString());
      if (ok) {
        setShowForm(false);
        const items = await fetchScheduleOverrides(app, selectedScheduleId, since, until);
        const sched = schedules.find((s) => s.id === selectedScheduleId);
        setOverrides(items.map((o) => ({ ...o, scheduleName: sched?.name ?? selectedScheduleId })));
      } else {
        setFormError("Failed to create override.");
      }
    } catch (e: any) {
      setFormError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(override: OverrideDetail) {
    const ok = await deleteOverride(app, override.scheduleId, override.id);
    if (ok) setOverrides((prev) => prev.filter((o) => o.id !== override.id));
  }

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>🔄 Overrides</h2>
            <div style={{ display: "flex", gap: 6, marginLeft: "auto", marginRight: 8 }}>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowWizard(true)}>
                Find Coverage
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => setShowForm((v) => !v)}>
                {showForm ? "Cancel" : "+ New Override"}
              </button>
            </div>
            <button className="modal-close" onClick={onClose}>✕</button>
          </div>
          <div className="modal-body">
            <div className="schedule-picker">
              <label>Schedule:</label>
              <select value={selectedScheduleId} onChange={(e) => setSelectedScheduleId((e.target as HTMLSelectElement).value)}>
                {schedules.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>

            {showForm && (
              <div className="create-form" style={{ marginBottom: 16 }}>
                {formError && <p className="error-banner">{formError}</p>}
                <div className="form-row">
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
                    <input type="datetime-local" value={formStart} onChange={(e) => setFormStart((e.target as HTMLInputElement).value)} />
                  </div>
                  <div className="form-field">
                    <label>End</label>
                    <input type="datetime-local" value={formEnd} onChange={(e) => setFormEnd((e.target as HTMLInputElement).value)} />
                  </div>
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button className="btn btn-primary" onClick={handleCreate} disabled={submitting || !formUser}>
                    {submitting ? "Creating…" : "Create Override"}
                  </button>
                </div>
              </div>
            )}

            {loading ? (
              <div className="loading-row"><span className="spinner" />Loading overrides…</div>
            ) : overrides.length === 0 ? (
              <p className="empty-state">No active or upcoming overrides for this schedule.</p>
            ) : (
              <div className="override-list">
                {overrides.map((o) => {
                  const color = userColor(o.user.id);
                  const initial = (o.user.name || "?")[0].toUpperCase();
                  return (
                    <div key={o.id} className="override-row">
                      <div className="or-user-dot" style={{ background: color, color: USER_COLOR_FG }}>{initial}</div>
                      <div className="or-info">
                        <div className="or-user">{o.user.name}</div>
                        <div className="or-meta">{fmtRange(o.start, o.end)}</div>
                      </div>
                      <div className="or-actions">
                        <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, background: "var(--surface0)", color: "var(--subtext0)" }}>
                          {new Date(o.start).getTime() <= Date.now() ? "Active" : "Upcoming"}
                        </span>
                        <button className="btn btn-ghost-danger btn-sm" onClick={() => handleDelete(o)} title="Delete override">✕</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          onClose={() => setShowWizard(false)}
          onDone={() => setShowWizard(false)}
        />
      )}
    </>
  );
}
