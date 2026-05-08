import React, { useState } from "react";
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

  function handleUserSelect(e: React.ChangeEvent<HTMLSelectElement>) {
    const select = e.target;
    const selected = Array.from(select.selectedOptions).map((o) => o.value);
    setDraft((d) => ({
      ...d,
      layers: [{ ...d.layers[0], user_ids: selected }],
    }));
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
              <label>Assign Users (hold Ctrl/Cmd to select multiple)</label>
              <select
                multiple
                size={Math.min(availableUsers.length, 6)}
                value={draft.layers[0].user_ids}
                onChange={handleUserSelect}
                style={{ minHeight: 80 }}
              >
                {availableUsers.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.email})
                  </option>
                ))}
              </select>
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
