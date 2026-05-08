import { useState } from "react";
import type { IncidentWorkflowFormData } from "../types.js";

interface Props {
  workflows: IncidentWorkflowFormData[];
  onChange: (workflows: IncidentWorkflowFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const EMPTY: IncidentWorkflowFormData = { name: "", description: "" };

export function PhaseIncidentWorkflows({ workflows, onChange, onNext, onBack, onSkip }: Props) {
  const [draft, setDraft] = useState<IncidentWorkflowFormData>(EMPTY);
  const [adding, setAdding] = useState(workflows.length === 0);

  function add() {
    if (!draft.name.trim()) return;
    onChange([...workflows, { ...draft }]);
    setDraft(EMPTY);
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(workflows.filter((_, i) => i !== idx));
  }

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Incident Workflows</h2>
        <p>Set up automated workflows that trigger when incidents occur.</p>
      </div>

      <div className="item-list">
        {workflows.map((w, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{w.name}</div>
              {w.description && <div className="item-row-detail">{w.description}</div>}
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-group">
            <label>Workflow Name *</label>
            <input
              type="text"
              placeholder="e.g. P1 Incident Response"
              value={draft.name}
              onChange={(e) => setDraft((d) => ({ ...d, name: (e.target as HTMLInputElement).value }))}
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              placeholder="Describe when and how this workflow triggers"
              value={draft.description}
              rows={2}
              onChange={(e) => setDraft((d) => ({ ...d, description: (e.target as HTMLTextAreaElement).value }))}
            />
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary btn-sm" onClick={add} disabled={!draft.name.trim()}>
              Add Workflow
            </button>
            {workflows.length > 0 && (
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
          + Add another workflow
        </button>
      )}

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={workflows.length === 0}
          >
            Review & Create →
          </button>
        </div>
      </div>
    </div>
  );
}
