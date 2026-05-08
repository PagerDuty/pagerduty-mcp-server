import { useState } from "react";
import type { TeamFormData } from "../types.js";

interface Props {
  teams: TeamFormData[];
  onChange: (teams: TeamFormData[]) => void;
  onNext: () => void;
  onSkip: () => void;
}

const EMPTY: TeamFormData = { name: "", description: "" };

export function PhaseTeams({ teams, onChange, onNext, onSkip }: Props) {
  const [draft, setDraft] = useState<TeamFormData>(EMPTY);
  const [adding, setAdding] = useState(teams.length === 0);

  function add() {
    if (!draft.name.trim()) return;
    onChange([...teams, { ...draft }]);
    setDraft(EMPTY);
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(teams.filter((_, i) => i !== idx));
  }

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Teams</h2>
        <p>Create the teams that will own services and escalation policies.</p>
      </div>

      <div className="item-list">
        {teams.map((t, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{t.name}</div>
              {t.description && <div className="item-row-detail">{t.description}</div>}
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-group">
            <label>Team Name *</label>
            <input
              type="text"
              placeholder="e.g. Platform Engineering"
              value={draft.name}
              onChange={(e) => setDraft((d) => ({ ...d, name: (e.target as HTMLInputElement).value }))}
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <input
              type="text"
              placeholder="Optional team description"
              value={draft.description}
              onChange={(e) => setDraft((d) => ({ ...d, description: (e.target as HTMLInputElement).value }))}
            />
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary btn-sm" onClick={add} disabled={!draft.name.trim()}>
              Add Team
            </button>
            {teams.length > 0 && (
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
          + Add another team
        </button>
      )}

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={teams.length === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
