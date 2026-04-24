import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { fetchScheduleDetail, fetchSchedules, fetchUsers, saveScheduleDetail } from "../api";
import type { Schedule, ScheduleDetail, ScheduleUser } from "../api";
import { USER_COLOR_FG, userColor } from "../utils/userColor";

interface Props {
  app: App;
  onClose: () => void;
}

function fmtRotation(seconds: number): string {
  const days = Math.round(seconds / 86400);
  return days === 7 ? "Weekly" : days === 1 ? "Daily" : `${days} days`;
}

export function SchedulesModal({ app, onClose }: Props) {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [filtered, setFiltered] = useState<Schedule[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ScheduleDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [editDetail, setEditDetail] = useState<ScheduleDetail | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const [userSearchQuery, setUserSearchQuery] = useState("");
  const [userSearchResults, setUserSearchResults] = useState<ScheduleUser[]>([]);
  const [addingToLayer, setAddingToLayer] = useState<string | null>(null);

  useEffect(() => {
    fetchSchedules(app).then((s) => { setSchedules(s); setFiltered(s); }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!query) { setFiltered(schedules); return; }
    const q = query.toLowerCase();
    setFiltered(schedules.filter((s) => s.name.toLowerCase().includes(q)));
  }, [query, schedules]);

  useEffect(() => {
    if (!selectedId) return;
    setDetailLoading(true);
    setDetail(null);
    setEditDetail(null);
    fetchScheduleDetail(app, selectedId)
      .then((d) => { setDetail(d); setEditDetail(d ? JSON.parse(JSON.stringify(d)) : null); })
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  useEffect(() => {
    if (!userSearchQuery || !addingToLayer) { setUserSearchResults([]); return; }
    const t = setTimeout(() => {
      fetchUsers(app, userSearchQuery).then(setUserSearchResults).catch(() => setUserSearchResults([]));
    }, 300);
    return () => clearTimeout(t);
  }, [userSearchQuery, addingToLayer]);

  function moveUser(layerId: string, fromIdx: number, toIdx: number) {
    if (!editDetail) return;
    const newDetail = JSON.parse(JSON.stringify(editDetail)) as ScheduleDetail;
    const layer = newDetail.layers.find((l) => l.id === layerId);
    if (!layer) return;
    const [user] = layer.users.splice(fromIdx, 1);
    layer.users.splice(toIdx, 0, user);
    setEditDetail(newDetail);
  }

  function removeUserFromLayer(layerId: string, userId: string) {
    if (!editDetail) return;
    const newDetail = JSON.parse(JSON.stringify(editDetail)) as ScheduleDetail;
    const layer = newDetail.layers.find((l) => l.id === layerId);
    if (!layer) return;
    layer.users = layer.users.filter((u) => u.id !== userId);
    setEditDetail(newDetail);
  }

  function addUserToLayer(layerId: string, user: ScheduleUser) {
    if (!editDetail) return;
    const newDetail = JSON.parse(JSON.stringify(editDetail)) as ScheduleDetail;
    const layer = newDetail.layers.find((l) => l.id === layerId);
    if (!layer || layer.users.find((u) => u.id === user.id)) return;
    layer.users.push(user);
    setEditDetail(newDetail);
    setAddingToLayer(null);
    setUserSearchQuery("");
    setUserSearchResults([]);
  }

  async function handleSave() {
    if (!editDetail) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const ok = await saveScheduleDetail(app, editDetail);
      if (ok) { setSaveSuccess(true); setDetail(JSON.parse(JSON.stringify(editDetail))); }
      else { setSaveError("Failed to save schedule."); }
    } catch (e: any) {
      setSaveError(e?.message ?? "Unexpected error");
    } finally {
      setSaving(false);
    }
  }

  const hasChanges = detail && editDetail && JSON.stringify(detail.layers.map((l) => l.users)) !== JSON.stringify(editDetail.layers.map((l) => l.users));

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          {selectedId && (
            <button className="detail-back" style={{ marginBottom: 0, marginRight: 4 }} onClick={() => { setSelectedId(null); setDetail(null); setEditDetail(null); }}>
              ← Back
            </button>
          )}
          <h2>📋 Schedules</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {!selectedId ? (
            <>
              <input className="search-input" placeholder="Search schedules…" value={query} onChange={(e) => setQuery((e.target as HTMLInputElement).value)} />
              {loading ? (
                <div className="loading-row"><span className="spinner" />Loading schedules…</div>
              ) : filtered.length === 0 ? (
                <p className="empty-state">No schedules found.</p>
              ) : (
                filtered.map((s) => (
                  <div key={s.id} className="list-row" onClick={() => setSelectedId(s.id)}>
                    <div className="list-row-title">{s.name}</div>
                    <div className="list-row-meta">{s.timeZone}</div>
                    <span className="list-row-chevron">›</span>
                  </div>
                ))
              )}
            </>
          ) : detailLoading ? (
            <div className="loading-row"><span className="spinner" />Loading schedule…</div>
          ) : editDetail ? (
            <>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{editDetail.name}</div>
                {editDetail.description && <div style={{ fontSize: 11, color: "var(--overlay0)", marginTop: 2 }}>{editDetail.description}</div>}
                <div style={{ fontSize: 10, color: "var(--overlay0)", marginTop: 2 }}>Timezone: {editDetail.timeZone}</div>
              </div>

              {saveError && <p className="error-banner">{saveError}</p>}
              {saveSuccess && <p style={{ color: "var(--green)", fontSize: 11, marginBottom: 10 }}>✓ Schedule saved successfully</p>}

              <p className="section-heading">Schedule Layers</p>
              {editDetail.layers.map((layer) => (
                <div key={layer.id} className="layer-card">
                  <div className="layer-header">
                    <span className="layer-title">{layer.name}</span>
                    <span className="layer-meta">{fmtRotation(layer.rotationSeconds)} rotation · {layer.users.length} users</span>
                  </div>
                  <div className="layer-users">
                    {layer.users.map((u, idx) => {
                      const color = userColor(u.id);
                      return (
                        <div key={u.id} className="layer-user-row">
                          <span className="layer-user-order">#{idx + 1}</span>
                          <div className="layer-user-dot" style={{ background: color, color: USER_COLOR_FG }}>{u.name[0]}</div>
                          <span className="layer-user-name">{u.name}</span>
                          <div style={{ display: "flex", gap: 2 }}>
                            {idx > 0 && (
                              <button className="btn btn-ghost btn-sm" onClick={() => moveUser(layer.id, idx, idx - 1)} title="Move up">↑</button>
                            )}
                            {idx < layer.users.length - 1 && (
                              <button className="btn btn-ghost btn-sm" onClick={() => moveUser(layer.id, idx, idx + 1)} title="Move down">↓</button>
                            )}
                            <button className="btn btn-ghost-danger btn-sm" onClick={() => removeUserFromLayer(layer.id, u.id)} title="Remove">✕</button>
                          </div>
                        </div>
                      );
                    })}
                    {addingToLayer === layer.id ? (
                      <div style={{ marginTop: 6 }}>
                        <input
                          className="user-search"
                          placeholder="Search users to add…"
                          value={userSearchQuery}
                          onChange={(e) => setUserSearchQuery((e.target as HTMLInputElement).value)}
                          autoFocus
                        />
                        {userSearchResults.length > 0 && (
                          <div className="user-list" style={{ maxHeight: 160 }}>
                            {userSearchResults.map((u) => (
                              <div key={u.id} className="user-option" onClick={() => addUserToLayer(layer.id, u)}>
                                <div className="user-option-dot" style={{ background: userColor(u.id), color: USER_COLOR_FG }}>{u.name[0]}</div>
                                <div className="user-option-info">
                                  <div className="user-name">{u.name}</div>
                                  <div className="user-email">{u.email}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        <button className="btn btn-secondary btn-sm" style={{ marginTop: 4 }} onClick={() => { setAddingToLayer(null); setUserSearchQuery(""); }}>Cancel</button>
                      </div>
                    ) : (
                      <button className="btn btn-ghost btn-sm" style={{ marginTop: 4, alignSelf: "flex-start" }} onClick={() => setAddingToLayer(layer.id)}>
                        + Add user
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {hasChanges && (
                <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                  <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                    {saving ? "Saving…" : "Save Changes"}
                  </button>
                  <button className="btn btn-secondary" onClick={() => setEditDetail(JSON.parse(JSON.stringify(detail!)))}>
                    Discard
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="empty-state">Failed to load schedule.</p>
          )}
        </div>
      </div>
    </div>
  );
}
