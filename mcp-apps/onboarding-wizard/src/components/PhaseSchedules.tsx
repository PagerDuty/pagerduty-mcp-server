import { useState } from "react";
import type { ScheduleFormData } from "../types.js";

interface Props {
  schedules: ScheduleFormData[];
  availableUsers: Array<{ id: string; name: string; email: string }>;
  onChange: (schedules: ScheduleFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const EMPTY: ScheduleFormData = {
  name: "",
  time_zone: "UTC",
  layers: [{ name: "Layer 1", rotation_type: "weekly", user_ids: [], handoff_time: "08:00" }],
};

export function PhaseSchedules({ schedules, availableUsers, onChange, onNext, onBack, onSkip }: Props) {
  const [draft, setDraft] = useState<ScheduleFormData>(EMPTY);
  const [adding, setAdding] = useState(schedules.length === 0);

  function add() {
    if (!draft.name.trim()) return;
    onChange([...schedules, { ...draft }]);
    setDraft(EMPTY);
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(schedules.filter((_, i) => i !== idx));
  }

  function toggleUser(userId: string) {
    const layer = draft.layers[0];
    const ids = layer.user_ids.includes(userId)
      ? layer.user_ids.filter((id) => id !== userId)
      : [...layer.user_ids, userId];
    setDraft((d) => ({ ...d, layers: [{ ...layer, user_ids: ids }] }));
  }

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Schedules</h2>
        <p>Define on-call rotations for your teams.</p>
      </div>

      <div className="item-list">
        {schedules.map((s, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{s.name}</div>
              <div className="item-row-detail">{s.time_zone} · {s.layers[0]?.rotation_type} · {s.layers[0]?.user_ids.length} user(s)</div>
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-row">
            <div className="form-group">
              <label>Schedule Name *</label>
              <input
                type="text"
                placeholder="Primary On-Call"
                value={draft.name}
                onChange={(e) => setDraft((d) => ({ ...d, name: (e.target as HTMLInputElement).value }))}
              />
            </div>
            <div className="form-group">
              <label>Time Zone</label>
              <input
                type="text"
                placeholder="UTC"
                value={draft.time_zone}
                onChange={(e) => setDraft((d) => ({ ...d, time_zone: (e.target as HTMLInputElement).value }))}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Rotation Type</label>
              <select
                value={draft.layers[0].rotation_type}
                onChange={(e) => setDraft((d) => ({
                  ...d,
                  layers: [{ ...d.layers[0], rotation_type: (e.target as HTMLSelectElement).value as "daily" | "weekly" }],
                }))}
              >
                <option value="weekly">Weekly</option>
                <option value="daily">Daily</option>
              </select>
            </div>
            <div className="form-group">
              <label>Handoff Time</label>
              <input
                type="time"
                value={draft.layers[0].handoff_time}
                onChange={(e) => setDraft((d) => ({
                  ...d,
                  layers: [{ ...d.layers[0], handoff_time: (e.target as HTMLInputElement).value }],
                }))}
              />
            </div>
          </div>
          {availableUsers.length > 0 && (
            <div className="form-group">
              <label>Assign Users</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
                {availableUsers.map((u) => {
                  const selected = draft.layers[0].user_ids.includes(u.id);
                  return (
                    <button
                      key={u.id}
                      className={`btn btn-sm ${selected ? "btn-primary" : "btn-secondary"}`}
                      onClick={() => toggleUser(u.id)}
                      type="button"
                    >
                      {u.name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary btn-sm" onClick={add} disabled={!draft.name.trim()}>
              Add Schedule
            </button>
            {schedules.length > 0 && (
              <button className="btn btn-secondary btn-sm" onClick={() => setAdding(false)}>
                Cancel
              </button>
            )}
          </div>
        </div>
      ) : (
        <button
          className="btn btn-secondary btn-sm"
          style={{ marginTop: 12 }}
          onClick={() => setAdding(true)}
        >
          + Add another schedule
        </button>
      )}

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={schedules.length === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
