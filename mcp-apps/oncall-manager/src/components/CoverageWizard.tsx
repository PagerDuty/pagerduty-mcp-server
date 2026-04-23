import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, fetchScheduleUsers } from "../api";
import type { OnCallShift, ScheduleUser } from "../api";

interface Props {
  app: App;
  shifts: OnCallShift[];         // user's own shifts to choose from
  preselectedShift?: OnCallShift;
  onClose: () => void;
  onDone: () => void;
}

function fmtRange(start: string, end: string): string {
  const fmt = (iso: string) =>
    new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  return `${fmt(start)} → ${fmt(end)}`;
}

export function CoverageWizard({ app, shifts, preselectedShift, onClose, onDone }: Props) {
  const [step, setStep] = useState<1 | 2 | 3>(preselectedShift ? 2 : 1);
  const [selectedShift, setSelectedShift] = useState<OnCallShift | null>(preselectedShift ?? null);
  const [users, setUsers] = useState<ScheduleUser[]>([]);
  const [userSearch, setUserSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState<ScheduleUser | null>(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (step === 2 && selectedShift) {
      setLoadingUsers(true);
      fetchScheduleUsers(app, selectedShift.scheduleId)
        .then(setUsers)
        .catch(() => setUsers([]))
        .finally(() => setLoadingUsers(false));
    }
  }, [step, selectedShift]);

  const filteredUsers = users.filter(
    (u) =>
      u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase()),
  );

  async function handleConfirm() {
    if (!selectedShift || !selectedUser) return;
    setSubmitting(true);
    setError(null);
    try {
      const ok = await createOverride(
        app,
        selectedShift.scheduleId,
        selectedUser.id,
        selectedShift.start,
        selectedShift.end,
      );
      if (ok) {
        onDone();
      } else {
        setError("Failed to create override. Please try again.");
      }
    } catch (e: any) {
      setError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  const stepLabel = ["Select shift", "Choose coverage", "Confirm"];

  return (
    <div className="wizard-overlay" onClick={onClose}>
      <div className="wizard-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="wizard-header">
          <h3>🔄 Find Coverage</h3>
          <button className="wizard-close" onClick={onClose}>✕</button>
        </div>

        <div className="wizard-steps">
          {[1, 2, 3].map((n, i) => (
            <>
              <div
                key={n}
                className={`wizard-step ${step === n ? "active" : step > n ? "done" : ""}`}
              >
                <span className="wizard-step-num">{step > n ? "✓" : n}</span>
                {stepLabel[i]}
              </div>
              {i < 2 && <span className="wizard-step-sep">›</span>}
            </>
          ))}
        </div>

        <div className="wizard-body">
          {step === 1 && (
            <div className="shift-list">
              {shifts.length === 0 && (
                <p className="empty-state">No upcoming shifts found.</p>
              )}
              {shifts.map((s, i) => (
                <div
                  key={i}
                  className={`shift-option ${selectedShift === s ? "selected" : ""}`}
                  onClick={() => setSelectedShift(s)}
                >
                  <div className="shift-sched">{s.scheduleName}</div>
                  <div className="shift-dates">{fmtRange(s.start, s.end)}</div>
                </div>
              ))}
            </div>
          )}

          {step === 2 && (
            <>
              {loadingUsers ? (
                <div className="loading-row"><span className="spinner" />Loading users…</div>
              ) : (
                <>
                  <input
                    className="user-search"
                    placeholder="Search by name or email…"
                    value={userSearch}
                    onChange={(e) => setUserSearch((e.target as HTMLInputElement).value)}
                  />
                  <div className="user-list">
                    {filteredUsers.length === 0 && (
                      <p className="empty-state">No users found.</p>
                    )}
                    {filteredUsers.map((u) => (
                      <div
                        key={u.id}
                        className={`user-option ${selectedUser?.id === u.id ? "selected" : ""}`}
                        onClick={() => setSelectedUser(u)}
                      >
                        <div className="user-name">{u.name}</div>
                        <div className="user-email">{u.email}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {step === 3 && selectedShift && selectedUser && (
            <>
              {error && <p className="error-banner">{error}</p>}
              <div className="confirm-card">
                <div className="confirm-row">
                  <span className="label">Schedule</span>
                  <span className="value">{selectedShift.scheduleName}</span>
                </div>
                <div className="confirm-row">
                  <span className="label">Period</span>
                  <span className="value">{fmtRange(selectedShift.start, selectedShift.end)}</span>
                </div>
                <div className="confirm-row">
                  <span className="label">Coverage by</span>
                  <span className="value">{selectedUser.name}</span>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="wizard-footer">
          <button
            className="btn btn-secondary"
            onClick={step === 1 ? onClose : () => setStep((s) => (s - 1) as 1 | 2 | 3)}
            disabled={submitting}
          >
            {step === 1 ? "Cancel" : "← Back"}
          </button>
          {step < 3 ? (
            <button
              className="btn btn-primary"
              onClick={() => setStep((s) => (s + 1) as 2 | 3)}
              disabled={
                (step === 1 && !selectedShift) ||
                (step === 2 && !selectedUser)
              }
            >
              Next →
            </button>
          ) : (
            <button
              className="btn btn-primary"
              onClick={handleConfirm}
              disabled={submitting}
            >
              {submitting ? "Creating…" : "Create Override"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
