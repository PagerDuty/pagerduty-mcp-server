import { useState } from "react";
import { CsvUpload } from "./CsvUpload.js";
import type { UserFormData } from "../types.js";

interface Props {
  users: UserFormData[];
  onChange: (users: UserFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const ROLES = [
  "user",
  "admin",
  "limited_user",
  "observer",
  "owner",
  "read_only_user",
  "restricted_access",
  "read_only_limited_user",
];

const EMPTY: UserFormData = { name: "", email: "", role: "user", time_zone: "UTC" };

export function PhaseUsers({ users, onChange, onNext, onBack, onSkip }: Props) {
  const [draft, setDraft] = useState<UserFormData>(EMPTY);
  const [adding, setAdding] = useState(users.length === 0);

  function add() {
    if (!draft.name.trim() || !draft.email.trim()) return;
    onChange([...users, { ...draft }]);
    setDraft(EMPTY);
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(users.filter((_, i) => i !== idx));
  }

  function handleCsvImport(imported: UserFormData[]) {
    const existing = new Set(users.map((u) => u.email));
    const deduped = imported.filter((u) => !existing.has(u.email));
    onChange([...users, ...deduped]);
  }

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Users</h2>
        <p>Add colleagues to onboard. Use the form or bulk-import via CSV.</p>
      </div>

      <div className="item-list">
        {users.map((u, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{u.name}</div>
              <div className="item-row-detail">{u.email} · {u.role} · {u.time_zone}</div>
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-row">
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                placeholder="Alice Johnson"
                value={draft.name}
                onChange={(e) => setDraft((d) => ({ ...d, name: (e.target as HTMLInputElement).value }))}
              />
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                placeholder="alice@example.com"
                value={draft.email}
                onChange={(e) => setDraft((d) => ({ ...d, email: (e.target as HTMLInputElement).value }))}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Role</label>
              <select
                value={draft.role}
                onChange={(e) => setDraft((d) => ({ ...d, role: (e.target as HTMLSelectElement).value }))}
              >
                {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
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
          <div style={{ display: "flex", gap: 8 }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={add}
              disabled={!draft.name.trim() || !draft.email.trim()}
            >
              Add User
            </button>
            {users.length > 0 && (
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
          + Add another user
        </button>
      )}

      <CsvUpload onImport={handleCsvImport} />

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={users.length === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
