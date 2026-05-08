import { useState } from "react";
import type { ServiceFormData } from "../types.js";

interface Props {
  services: ServiceFormData[];
  availableEscalationPolicies: Array<{ id: string; name: string }>;
  onChange: (services: ServiceFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const EMPTY: ServiceFormData = {
  name: "",
  description: "",
  escalation_policy_id: "",
  escalation_policy_name: "",
};

export function PhaseServices({
  services,
  availableEscalationPolicies,
  onChange,
  onNext,
  onBack,
  onSkip,
}: Props) {
  const [draft, setDraft] = useState<ServiceFormData>(EMPTY);
  const [adding, setAdding] = useState(services.length === 0);

  function add() {
    if (!draft.name.trim() || !draft.escalation_policy_id) return;
    onChange([...services, { ...draft }]);
    setDraft(EMPTY);
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(services.filter((_, i) => i !== idx));
  }

  const epName = (id: string) =>
    availableEscalationPolicies.find((ep) => ep.id === id)?.name ?? id;

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Services</h2>
        <p>Create services that represent the things you monitor in PagerDuty.</p>
      </div>

      <div className="item-list">
        {services.map((s, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{s.name}</div>
              <div className="item-row-detail">{epName(s.escalation_policy_id)}</div>
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-row">
            <div className="form-group">
              <label>Service Name *</label>
              <input
                type="text"
                placeholder="Payment Service"
                value={draft.name}
                onChange={(e) => setDraft((d) => ({ ...d, name: (e.target as HTMLInputElement).value }))}
              />
            </div>
            <div className="form-group">
              <label>Escalation Policy *</label>
              <select
                value={draft.escalation_policy_id}
                onChange={(e) => {
                  const sel = e.target as HTMLSelectElement;
                  const epName = sel.options[sel.selectedIndex]?.text ?? "";
                  setDraft((d) => ({ ...d, escalation_policy_id: sel.value, escalation_policy_name: epName }));
                }}
              >
                <option value="">-- select --</option>
                {availableEscalationPolicies.map((ep) => (
                  <option key={ep.id} value={ep.id}>{ep.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Description</label>
            <input
              type="text"
              placeholder="Optional description"
              value={draft.description}
              onChange={(e) => setDraft((d) => ({ ...d, description: (e.target as HTMLInputElement).value }))}
            />
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={add}
              disabled={!draft.name.trim() || !draft.escalation_policy_id}
            >
              Add Service
            </button>
            {services.length > 0 && (
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
          + Add another service
        </button>
      )}

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={services.length === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
