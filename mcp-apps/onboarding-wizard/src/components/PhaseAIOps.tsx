import { useState } from "react";
import { BestPracticesPanel } from "./BestPracticesPanel.js";
import type { AlertGroupingFormData } from "../types.js";

interface Props {
  groupings: AlertGroupingFormData[];
  availableServices: Array<{ id: string; name: string }>;
  onChange: (groupings: AlertGroupingFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const AIOPS_TIPS = [
  { icon: "🧠", text: "Intelligent (recommended): ML-based grouping with no manual config — learns from your incident patterns automatically." },
  { icon: "⏱️", text: "Time-based: groups alerts within a fixed time window (60–3600 seconds). Good when incidents reliably occur in bursts." },
  { icon: "🔍", text: "Content-based: groups alerts by matching summary keywords. Good when alerts have consistent, structured content." },
  { icon: "✅", text: "Start with Intelligent for new services — zero config, works immediately. You can switch to another type later." },
];

const EMPTY: AlertGroupingFormData = {
  service_id: "",
  type: "intelligent",
  timeout: 300,
};

export function PhaseAIOps({
  groupings,
  availableServices,
  onChange,
  onNext,
  onBack,
  onSkip,
}: Props) {
  const [draft, setDraft] = useState<AlertGroupingFormData>(EMPTY);
  const [adding, setAdding] = useState(groupings.length === 0);

  function add() {
    if (!draft.service_id) return;
    onChange([...groupings, { ...draft }]);
    setDraft(EMPTY);
    setAdding(false);
  }

  function remove(idx: number) {
    onChange(groupings.filter((_, i) => i !== idx));
  }

  const svcName = (id: string) =>
    availableServices.find((s) => s.id === id)?.name ?? id;

  const unassigned = availableServices.filter(
    (s) => !groupings.some((g) => g.service_id === s.id),
  );

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>AIOps — Alert Grouping</h2>
        <p>Configure intelligent alert grouping to reduce noise on your services.</p>
      </div>

      <BestPracticesPanel phase="AIOps" tips={AIOPS_TIPS} />

      <div className="item-list">
        {groupings.map((g, i) => (
          <div key={i} className="item-row">
            <div className="item-row-main">
              <div className="item-row-name">{svcName(g.service_id)}</div>
              <div className="item-row-detail">{g.type}{g.type !== "intelligent" ? ` · ${g.timeout}s` : ""}</div>
            </div>
            <button className="btn btn-sm btn-danger" onClick={() => remove(i)}>Remove</button>
          </div>
        ))}
      </div>

      {adding ? (
        <div className="add-section">
          <div className="form-row">
            <div className="form-group">
              <label>Service *</label>
              <select
                value={draft.service_id}
                onChange={(e) => setDraft((d) => ({ ...d, service_id: (e.target as HTMLSelectElement).value }))}
              >
                <option value="">-- select --</option>
                {(draft.service_id ? availableServices : unassigned).map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Grouping Type</label>
              <select
                value={draft.type}
                onChange={(e) => setDraft((d) => ({ ...d, type: (e.target as HTMLSelectElement).value as AlertGroupingFormData["type"] }))}
              >
                <option value="intelligent">Intelligent (ML-based)</option>
                <option value="time">Time-based</option>
                <option value="content_based">Content-based</option>
              </select>
            </div>
          </div>
          {draft.type !== "intelligent" && (
            <div className="form-group">
              <label>Time Window (seconds)</label>
              <input
                type="number"
                min={60}
                max={3600}
                value={draft.timeout ?? 300}
                onChange={(e) => setDraft((d) => ({ ...d, timeout: parseInt((e.target as HTMLInputElement).value) || 300 }))}
              />
            </div>
          )}
          <div style={{ display: "flex", gap: 8 }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={add}
              disabled={!draft.service_id}
            >
              Add Grouping
            </button>
            {groupings.length > 0 && (
              <button className="btn btn-secondary btn-sm" onClick={() => setAdding(false)}>
                Cancel
              </button>
            )}
          </div>
        </div>
      ) : unassigned.length > 0 ? (
        <button
          className="btn btn-secondary btn-sm"
          style={{ marginTop: 12 }}
          onClick={() => setAdding(true)}
        >
          + Configure another service
        </button>
      ) : null}

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={groupings.length === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
