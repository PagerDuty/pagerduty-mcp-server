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

const ROTATION_OPTIONS = [
  { label: "Daily (24h)", value: 86400 },
  { label: "Weekly (7d)", value: 604800 },
];

const EMPTY: ScheduleFormData = {
  name: "",
  time_zone: "UTC",
  layers: [{ name: "Layer 1", rotation_turn_length_seconds: 604800, user_ids: [], handoff_time: "08:00" }],
};

export function PhaseSchedules({ schedules, availableUsers, onChange, onNext, onBack, onSkip }: Props) {
  const [draft, setDraft] = useState<ScheduleFormData>(EMPTY);
  const [adding, setAdding] = useState(schedules.length === 0);

  function add() {
    if (!draft.name.trim()) return;
    onChange([...schedules, { ...draft }]);
    setDraft({ ...EMPTY, layers: [{ ...EMPTY.layers[0] }] });
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(schedules.filter((_, i) => i !== idx));
  }

  const rotationLabel = (s: number) =>
    ROTATION_OPTIONS.find((o) => o.value === s)?.label ?? `${s}s`;

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
              <div className="item-row-detail">
                {s.time_zone} · {rotationLabel(s.layers[0]?.rotation_turn_length_seconds)} · {s.layers[0]?.user_ids.length} user(s)
              </div>
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
              <label>Rotation Length</label>
              <select
                value={draft.layers[0].rotation_turn_length_seconds}
                onChange={(e) => setDraft((d) => ({
                  ...d,
                  layers: [{ ...d.layers[0], rotation_turn_length_seconds: parseInt((e.target as HTMLSelectElement).value) }],
                }))}
              >
                {ROTATION_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
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
              <label>
                Assign Users
                {draft.layers[0].user_ids.length > 0 && (
                  <span className="user-count-badge">{draft.layers[0].user_ids.length} selected</span>
                )}
              </label>
              <div className="user-checkbox-list">
                {availableUsers.map((u) => {
                  const checked = draft.layers[0].user_ids.includes(u.id);
                  return (
                    <label key={u.id} className={`user-checkbox-item${checked ? " checked" : ""}`}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => {
                          const ids = checked
                            ? draft.layers[0].user_ids.filter((id) => id !== u.id)
                            : [...draft.layers[0].user_ids, u.id];
                          setDraft((d) => ({ ...d, layers: [{ ...d.layers[0], user_ids: ids }] }));
                        }}
                      />
                      <span className="user-checkbox-name">{u.name}</span>
                      <span className="user-checkbox-email">{u.email}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
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
          <button className="btn btn-primary" onClick={onNext} disabled={schedules.length === 0}>
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
