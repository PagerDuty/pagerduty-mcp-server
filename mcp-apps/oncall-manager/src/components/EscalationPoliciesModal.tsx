import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import {
  createEscalationPolicy,
  deleteEscalationPolicy,
  fetchEscalationPolicies,
  fetchEscalationPolicy,
  fetchSchedules,
  fetchUsers,
  updateEscalationPolicy,
} from "../api";
import type { EscalationPolicy, EscalationRule, Schedule, ScheduleUser } from "../api";

interface Props {
  app: App;
  onClose: () => void;
}

function newRule(): EscalationRule {
  return { escalation_delay_in_minutes: 30, targets: [] };
}

function newPolicy(): Pick<EscalationPolicy, "name" | "description" | "num_loops" | "escalation_rules"> {
  return { name: "", description: null, num_loops: 0, escalation_rules: [newRule()] };
}

export function EscalationPoliciesModal({ app, onClose }: Props) {
  const [policies, setPolicies] = useState<EscalationPolicy[]>([]);
  const [filtered, setFiltered] = useState<EscalationPolicy[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editPolicy, setEditPolicy] = useState<EscalationPolicy | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createDraft, setCreateDraft] = useState(newPolicy());

  const [targetSearch, setTargetSearch] = useState("");
  const [targetSearchResults, setTargetSearchResults] = useState<Array<{ id: string; name: string; type: "user_reference" | "schedule_reference" }>>([]);
  const [addingTargetToRule, setAddingTargetToRule] = useState<number | null>(null);

  const [cachedSchedules, setCachedSchedules] = useState<Schedule[]>([]);
  const [cachedUsers, setCachedUsers] = useState<ScheduleUser[]>([]);

  useEffect(() => {
    fetchEscalationPolicies(app).then((p) => { setPolicies(p); setFiltered(p); }).finally(() => setLoading(false));
    fetchSchedules(app).then(setCachedSchedules).catch(() => {});
    fetchUsers(app).then(setCachedUsers).catch(() => {});
  }, []);

  useEffect(() => {
    if (!query) { setFiltered(policies); return; }
    const q = query.toLowerCase();
    setFiltered(policies.filter((p) => p.name.toLowerCase().includes(q)));
  }, [query, policies]);

  useEffect(() => {
    if (!selectedId) return;
    setDetailLoading(true);
    setEditPolicy(null);
    fetchEscalationPolicy(app, selectedId)
      .then((p) => setEditPolicy(p ? JSON.parse(JSON.stringify(p)) : null))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  useEffect(() => {
    if (!targetSearch || addingTargetToRule === null) { setTargetSearchResults([]); return; }
    const q = targetSearch.toLowerCase();
    const users = cachedUsers.filter((u) => u.name.toLowerCase().includes(q)).map((u) => ({ id: u.id, name: u.name, type: "user_reference" as const }));
    const scheds = cachedSchedules.filter((s) => s.name.toLowerCase().includes(q)).map((s) => ({ id: s.id, name: s.name, type: "schedule_reference" as const }));
    setTargetSearchResults([...users, ...scheds].slice(0, 10));
  }, [targetSearch, addingTargetToRule, cachedUsers, cachedSchedules]);

  function updateRule(idx: number, patch: Partial<EscalationRule>) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    rules[idx] = { ...rules[idx], ...patch };
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  function addRule() {
    if (!editPolicy) return;
    setEditPolicy({ ...editPolicy, escalation_rules: [...editPolicy.escalation_rules, newRule()] });
  }

  function removeRule(idx: number) {
    if (!editPolicy) return;
    const rules = editPolicy.escalation_rules.filter((_, i) => i !== idx);
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  function moveRule(from: number, to: number) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    const [r] = rules.splice(from, 1);
    rules.splice(to, 0, r);
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  function addTarget(ruleIdx: number, t: { id: string; name: string; type: "user_reference" | "schedule_reference" }) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    const rule = rules[ruleIdx];
    if (rule.targets.find((x) => x.id === t.id)) return;
    rules[ruleIdx] = { ...rule, targets: [...rule.targets, { id: t.id, type: t.type, summary: t.name }] };
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
    setAddingTargetToRule(null);
    setTargetSearch("");
  }

  function removeTarget(ruleIdx: number, targetId: string) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    rules[ruleIdx] = { ...rules[ruleIdx], targets: rules[ruleIdx].targets.filter((t) => t.id !== targetId) };
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  async function handleSave() {
    if (!editPolicy) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const ok = await updateEscalationPolicy(app, editPolicy.id, editPolicy);
      if (ok) { setSaveSuccess(true); setPolicies((prev) => prev.map((p) => (p.id === editPolicy.id ? editPolicy : p))); }
      else { setSaveError("Failed to save."); }
    } catch (e: any) {
      setSaveError(e?.message ?? "Unexpected error");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!editPolicy) return;
    if (!confirm(`Delete "${editPolicy.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      const ok = await deleteEscalationPolicy(app, editPolicy.id);
      if (ok) {
        setPolicies((prev) => prev.filter((p) => p.id !== editPolicy.id));
        setSelectedId(null);
        setEditPolicy(null);
      }
    } finally {
      setDeleting(false);
    }
  }

  async function handleCreate() {
    setSaving(true);
    setSaveError(null);
    try {
      const created = await createEscalationPolicy(app, createDraft);
      if (created) {
        setPolicies((prev) => [...prev, created]);
        setShowCreateForm(false);
        setCreateDraft(newPolicy());
        setSelectedId(created.id);
      } else {
        setSaveError("Failed to create policy.");
      }
    } catch (e: any) {
      setSaveError(e?.message ?? "Unexpected error");
    } finally {
      setSaving(false);
    }
  }

  function renderRules(
    rules: EscalationRule[],
    onUpdateRule: (idx: number, patch: Partial<EscalationRule>) => void,
    onAddRule: () => void,
    onRemoveRule: (idx: number) => void,
    onMoveRule: (from: number, to: number) => void,
    onAddTarget: (ruleIdx: number, t: { id: string; name: string; type: "user_reference" | "schedule_reference" }) => void,
    onRemoveTarget: (ruleIdx: number, targetId: string) => void,
  ) {
    return (
      <>
        {rules.map((rule, ruleIdx) => (
          <div key={ruleIdx} className="ep-rule-card">
            <div className="ep-rule-header">
              <span className="ep-rule-num">{ruleIdx + 1}</span>
              <span className="ep-rule-delay">
                Escalate after{" "}
                <input
                  type="number"
                  min={1}
                  max={999}
                  value={rule.escalation_delay_in_minutes}
                  onChange={(e) => onUpdateRule(ruleIdx, { escalation_delay_in_minutes: parseInt((e.target as HTMLInputElement).value) || 30 })}
                  style={{ width: 48, background: "var(--surface1)", border: "none", borderRadius: 3, color: "var(--text)", padding: "1px 4px", fontSize: 11, textAlign: "center" }}
                />{" "}
                minutes
              </span>
              <div style={{ display: "flex", gap: 2 }}>
                {ruleIdx > 0 && <button className="btn btn-ghost btn-sm" onClick={() => onMoveRule(ruleIdx, ruleIdx - 1)}>↑</button>}
                {ruleIdx < rules.length - 1 && <button className="btn btn-ghost btn-sm" onClick={() => onMoveRule(ruleIdx, ruleIdx + 1)}>↓</button>}
                <button className="btn btn-ghost-danger btn-sm" onClick={() => onRemoveRule(ruleIdx)}>✕</button>
              </div>
            </div>
            <div className="ep-rule-body">
              {rule.targets.map((t) => (
                <div key={t.id} className="ep-target-row">
                  <span className="ep-target-icon">{t.type === "user_reference" ? "👤" : "📅"}</span>
                  <span className="ep-target-name">{t.summary}</span>
                  <span className="ep-target-type">{t.type === "user_reference" ? "User" : "Schedule"}</span>
                  <button className="btn btn-ghost-danger btn-sm" onClick={() => onRemoveTarget(ruleIdx, t.id)}>✕</button>
                </div>
              ))}
              {rule.targets.length === 0 && <p style={{ fontSize: 10, color: "var(--overlay0)", padding: "4px 0" }}>No targets — add a user or schedule below</p>}

              {addingTargetToRule === ruleIdx ? (
                <div style={{ marginTop: 6 }}>
                  <input
                    className="user-search"
                    placeholder="Search users or schedules…"
                    value={targetSearch}
                    onChange={(e) => setTargetSearch((e.target as HTMLInputElement).value)}
                    autoFocus
                  />
                  {targetSearchResults.length > 0 && (
                    <div className="user-list" style={{ maxHeight: 140 }}>
                      {targetSearchResults.map((t) => (
                        <div key={t.id} className="user-option" onClick={() => onAddTarget(ruleIdx, t)}>
                          <span style={{ fontSize: 14 }}>{t.type === "user_reference" ? "👤" : "📅"}</span>
                          <div className="user-option-info"><div className="user-name">{t.name}</div></div>
                        </div>
                      ))}
                    </div>
                  )}
                  <button className="btn btn-secondary btn-sm" style={{ marginTop: 4 }} onClick={() => { setAddingTargetToRule(null); setTargetSearch(""); }}>Cancel</button>
                </div>
              ) : (
                <button className="btn btn-ghost btn-sm" style={{ marginTop: 4, alignSelf: "flex-start" }} onClick={() => setAddingTargetToRule(ruleIdx)}>
                  + Add target
                </button>
              )}
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={onAddRule}>+ Add escalation rule</button>
      </>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          {selectedId && (
            <button className="detail-back" style={{ marginBottom: 0, marginRight: 4 }} onClick={() => { setSelectedId(null); setEditPolicy(null); setSaveSuccess(false); }}>
              ← Back
            </button>
          )}
          <h2>📊 Escalation Policies</h2>
          {!selectedId && (
            <button className="btn btn-primary btn-sm" style={{ marginLeft: "auto", marginRight: 8 }} onClick={() => setShowCreateForm((v) => !v)}>
              {showCreateForm ? "Cancel" : "+ New Policy"}
            </button>
          )}
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {!selectedId ? (
            <>
              {showCreateForm && (
                <div className="create-form" style={{ marginBottom: 16 }}>
                  <p className="section-heading">New Escalation Policy</p>
                  {saveError && <p className="error-banner">{saveError}</p>}
                  <div className="form-row">
                    <div className="form-field">
                      <label>Name *</label>
                      <input type="text" value={createDraft.name} onChange={(e) => setCreateDraft({ ...createDraft, name: (e.target as HTMLInputElement).value })} placeholder="Policy name" />
                    </div>
                    <div className="form-field" style={{ maxWidth: 100 }}>
                      <label>Loops</label>
                      <input type="number" min={0} max={9} value={createDraft.num_loops} onChange={(e) => setCreateDraft({ ...createDraft, num_loops: parseInt((e.target as HTMLInputElement).value) || 0 })} />
                    </div>
                  </div>
                  <div className="form-field">
                    <label>Description</label>
                    <textarea value={createDraft.description ?? ""} onChange={(e) => setCreateDraft({ ...createDraft, description: (e.target as HTMLTextAreaElement).value || null })} rows={2} />
                  </div>
                  {renderRules(
                    createDraft.escalation_rules,
                    (i, p) => { const r = [...createDraft.escalation_rules]; r[i] = { ...r[i], ...p }; setCreateDraft({ ...createDraft, escalation_rules: r }); },
                    () => setCreateDraft({ ...createDraft, escalation_rules: [...createDraft.escalation_rules, newRule()] }),
                    (i) => setCreateDraft({ ...createDraft, escalation_rules: createDraft.escalation_rules.filter((_, idx) => idx !== i) }),
                    (from, to) => { const r = [...createDraft.escalation_rules]; const [x] = r.splice(from, 1); r.splice(to, 0, x); setCreateDraft({ ...createDraft, escalation_rules: r }); },
                    (ruleIdx, t) => { const r = [...createDraft.escalation_rules]; r[ruleIdx] = { ...r[ruleIdx], targets: [...r[ruleIdx].targets, { id: t.id, type: t.type, summary: t.name }] }; setCreateDraft({ ...createDraft, escalation_rules: r }); setAddingTargetToRule(null); setTargetSearch(""); },
                    (ruleIdx, tid) => { const r = [...createDraft.escalation_rules]; r[ruleIdx] = { ...r[ruleIdx], targets: r[ruleIdx].targets.filter((t) => t.id !== tid) }; setCreateDraft({ ...createDraft, escalation_rules: r }); },
                  )}
                  <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
                    <button className="btn btn-primary" onClick={handleCreate} disabled={saving || !createDraft.name}>
                      {saving ? "Creating…" : "Create Policy"}
                    </button>
                  </div>
                </div>
              )}

              <input className="search-input" placeholder="Search escalation policies…" value={query} onChange={(e) => setQuery((e.target as HTMLInputElement).value)} />
              {loading ? (
                <div className="loading-row"><span className="spinner" />Loading policies…</div>
              ) : filtered.length === 0 ? (
                <p className="empty-state">No escalation policies found.</p>
              ) : (
                filtered.map((p) => (
                  <div key={p.id} className="list-row" onClick={() => setSelectedId(p.id)}>
                    <div className="list-row-title">{p.name}</div>
                    <div className="list-row-meta">{p.escalation_rules.length} rule{p.escalation_rules.length !== 1 ? "s" : ""}{p.services.length > 0 ? ` · ${p.services.length} service${p.services.length !== 1 ? "s" : ""}` : ""}</div>
                    <span className="list-row-chevron">›</span>
                  </div>
                ))
              )}
            </>
          ) : detailLoading ? (
            <div className="loading-row"><span className="spinner" />Loading policy…</div>
          ) : editPolicy ? (
            <>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{editPolicy.name}</div>
                {editPolicy.description && <div style={{ fontSize: 11, color: "var(--overlay0)", marginTop: 2 }}>{editPolicy.description}</div>}
                <div style={{ fontSize: 10, color: "var(--overlay0)", marginTop: 2 }}>
                  Loops: {editPolicy.num_loops} · {editPolicy.services.length} service{editPolicy.services.length !== 1 ? "s" : ""}
                  {editPolicy.teams.length > 0 ? ` · ${editPolicy.teams.map((t) => t.summary).join(", ")}` : ""}
                </div>
              </div>

              {saveError && <p className="error-banner">{saveError}</p>}
              {saveSuccess && <p style={{ color: "var(--green)", fontSize: 11, marginBottom: 10 }}>✓ Policy saved successfully</p>}

              <p className="section-heading">Escalation Rules</p>
              {renderRules(
                editPolicy.escalation_rules,
                updateRule,
                addRule,
                removeRule,
                moveRule,
                addTarget,
                removeTarget,
              )}

              <hr className="divider" />
              <div style={{ display: "flex", gap: 8, justifyContent: "space-between" }}>
                <button className="btn btn-danger btn-sm" onClick={handleDelete} disabled={deleting}>
                  {deleting ? "Deleting…" : "Delete Policy"}
                </button>
                <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                  {saving ? "Saving…" : "Save Changes"}
                </button>
              </div>
            </>
          ) : (
            <p className="empty-state">Failed to load policy.</p>
          )}
        </div>
      </div>
    </div>
  );
}
