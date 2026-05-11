import { useState } from "react";
import { BestPracticesPanel } from "./BestPracticesPanel.js";
import type { EscalationPolicyFormData, EscalationRule } from "../types.js";

interface Props {
  policies: EscalationPolicyFormData[];
  availableUsers: Array<{ id: string; name: string }>;
  availableSchedules: Array<{ id: string; name: string }>;
  onChange: (policies: EscalationPolicyFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const EP_TIPS = [
  { icon: "📛", text: "Name format: \"TeamName EP\" (e.g., \"Payments Team EP\")." },
  { icon: "📶", text: "Always use 3 levels: Level 1 = Primary on-call schedule → Level 2 = Backup person or schedule → Level 3 = Engineering manager. Never rely on a single escalation level." },
  { icon: "⏱️", text: "Timeout guidelines: 5 min for revenue-critical services (payments, login) · 10–15 min for standard production services. Maximum 15 min unless specifically required." },
  { icon: "🔁", text: "Set repeats to at least 2, recommended 3. This ensures incidents don't go unnoticed if all levels miss the page." },
];

const EMPTY_RULE: EscalationRule = { escalation_delay_in_minutes: 30, target_type: "user", target_id: "" };

const EMPTY: EscalationPolicyFormData = {
  name: "",
  description: "",
  num_loops: 0,
  rules: [{ ...EMPTY_RULE }],
};

export function PhaseEscalationPolicies({
  policies,
  availableUsers,
  availableSchedules,
  onChange,
  onNext,
  onBack,
  onSkip,
}: Props) {
  const [draft, setDraft] = useState<EscalationPolicyFormData>(EMPTY);
  const [adding, setAdding] = useState(policies.length === 0);

  function add() {
    if (!draft.name.trim()) return;
    onChange([...policies, { ...draft }]);
    setDraft({ ...EMPTY, rules: [{ ...EMPTY_RULE }] });
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(policies.filter((_, i) => i !== idx));
  }

  function updateRule(idx: number, patch: Partial<EscalationRule>) {
    setDraft((d) => ({
      ...d,
      rules: d.rules.map((r, i) => (i === idx ? { ...r, ...patch } : r)),
    }));
  }

  function addRule() {
    setDraft((d) => ({ ...d, rules: [...d.rules, { ...EMPTY_RULE }] }));
  }

  function removeRule(idx: number) {
    setDraft((d) => ({ ...d, rules: d.rules.filter((_, i) => i !== idx) }));
  }

  const targets = (type: "user" | "schedule") =>
    type === "user" ? availableUsers : availableSchedules;

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Escalation Policies</h2>
        <p>Define who gets paged and in what order when incidents occur.</p>
      </div>

      <BestPracticesPanel phase="Escalation Policies" tips={EP_TIPS} />

      <div className="item-list">
        {policies.map((p, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{p.name}</div>
              <div className="item-row-detail">{p.rules.length} rule(s) · loops: {p.num_loops}</div>
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-row">
            <div className="form-group">
              <label>Policy Name *</label>
              <input
                type="text"
                placeholder="Default Escalation Policy"
                value={draft.name}
                onChange={(e) => setDraft((d) => ({ ...d, name: (e.target as HTMLInputElement).value }))}
              />
            </div>
            <div className="form-group">
              <label>Repeat (num_loops)</label>
              <input
                type="number"
                min={0}
                max={9}
                value={draft.num_loops}
                onChange={(e) => setDraft((d) => ({ ...d, num_loops: parseInt((e.target as HTMLInputElement).value) || 0 }))}
              />
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

          <div className="card-title" style={{ marginTop: 12 }}>Escalation Rules</div>
          {draft.rules.map((rule, ri) => (
            <div key={ri} className="card" style={{ marginBottom: 8 }}>
              <div className="form-row">
                <div className="form-group">
                  <label>Escalate after (min)</label>
                  <input
                    type="number"
                    min={0}
                    value={rule.escalation_delay_in_minutes}
                    onChange={(e) => updateRule(ri, { escalation_delay_in_minutes: parseInt((e.target as HTMLInputElement).value) || 0 })}
                  />
                </div>
                <div className="form-group">
                  <label>Target Type</label>
                  <select
                    value={rule.target_type}
                    onChange={(e) => updateRule(ri, { target_type: (e.target as HTMLSelectElement).value as "user" | "schedule", target_id: "" })}
                  >
                    <option value="user">User</option>
                    <option value="schedule">Schedule</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Target</label>
                <select
                  value={rule.target_id}
                  onChange={(e) => updateRule(ri, { target_id: (e.target as HTMLSelectElement).value })}
                >
                  <option value="">-- select --</option>
                  {targets(rule.target_type).map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
              {draft.rules.length > 1 && (
                <button className="btn btn-sm btn-danger" onClick={() => removeRule(ri)}>
                  Remove rule
                </button>
              )}
            </div>
          ))}
          <button className="btn btn-secondary btn-sm" onClick={addRule} style={{ marginBottom: 12 }}>
            + Add rule
          </button>

          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary btn-sm" onClick={add} disabled={!draft.name.trim()}>
              Add Policy
            </button>
            {policies.length > 0 && (
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
          + Add another policy
        </button>
      )}

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={policies.length === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
