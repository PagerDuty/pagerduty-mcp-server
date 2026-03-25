import { useEffect } from "react";
import type { UserCompensationRecord } from "../api";

interface Props {
  record: UserCompensationRecord;
  onClose: () => void;
}

function formatDateTime(iso: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  const rem = m % 60;
  return rem > 0 ? `${h}h ${rem}m` : `${h}h`;
}

export function UserDetailModal({ record, onClose }: Props) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const sortedIncidents = record.incidents
    .slice()
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  const totalIntrs = record.totalInterruptions;
  const hasOutsideData = record.outsideHours > 0 || record.weekendHours > 0 || record.holidayHours > 0;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>

        {/* Modal header */}
        <div className="modal-header">
          <div className="modal-header-info">
            <div className="modal-name">{record.userName}</div>
            {record.teamName && (
              <div className="modal-team">{record.teamName}</div>
            )}
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {/* Stats bar */}
        <div className="modal-stats">
          <div className="modal-stat">
            <div className="modal-stat-value">{record.scheduledHours.toFixed(1)}h</div>
            <div className="modal-stat-label">Oncall Hrs</div>
          </div>
          {record.scheduledHoursL1 > 0 && (
            <div className="modal-stat">
              <div className="modal-stat-value">{record.scheduledHoursL1.toFixed(1)}h</div>
              <div className="modal-stat-label">L1 Hrs</div>
            </div>
          )}
          <div className="modal-stat">
            <div className="modal-stat-value">{record.incidentCount}</div>
            <div className="modal-stat-label">Incidents</div>
          </div>
          <div className="modal-stat">
            <div className="modal-stat-value">{record.incidentHours.toFixed(1)}h</div>
            <div className="modal-stat-label">Engaged Hrs</div>
          </div>
          <div className="modal-stat">
            <div className="modal-stat-value">{record.interruptionRate.toFixed(2)}</div>
            <div className="modal-stat-label">Rate /hr</div>
          </div>
          {record.meanTimeToAckSeconds > 0 && (
            <div className="modal-stat">
              <div className="modal-stat-value">{formatDuration(record.meanTimeToAckSeconds)}</div>
              <div className="modal-stat-label">Avg Ack</div>
            </div>
          )}
        </div>

        {/* Interruption breakdown strip */}
        {totalIntrs > 0 && (
          <div className="modal-ooh-strip">
            <span className="modal-ooh-item">
              <span className="modal-ooh-key">Total interruptions</span>
              <span className="modal-ooh-val">{totalIntrs}</span>
            </span>
            <span className="modal-ooh-sep">·</span>
            <span className="modal-ooh-item">
              <span className="modal-ooh-key">Business hrs</span>
              <span className="modal-ooh-val">{record.businessHourInterruptions}</span>
            </span>
            <span className="modal-ooh-sep">·</span>
            <span className="modal-ooh-item">
              <span className="modal-ooh-key ooh-label">Off-hours</span>
              <span className="modal-ooh-val ooh-value">{record.offHourInterruptions}</span>
            </span>
            <span className="modal-ooh-sep">·</span>
            <span className="modal-ooh-item">
              <span className="modal-ooh-key ooh-label">Sleep hours</span>
              <span className="modal-ooh-val ooh-value">{record.sleepHourInterruptions}</span>
            </span>
          </div>
        )}

        {/* Outside business hours breakdown */}
        {hasOutsideData && (
          <div className="modal-bh-section">
            <div className="modal-bh-title">Outside Business Hours Breakdown</div>
            <div className="modal-bh-grid">
              <div className="modal-bh-stat">
                <div className="modal-bh-value bh-value">{record.outsideHours.toFixed(1)}h</div>
                <div className="modal-bh-label">Total Outside BH</div>
              </div>
              <div className="modal-bh-stat">
                <div className="modal-bh-value">{record.weekendHours.toFixed(1)}h</div>
                <div className="modal-bh-label">Weekend Hours</div>
              </div>
              <div className="modal-bh-stat">
                <div className="modal-bh-value">
                  {record.holidayHours > 0 ? `${record.holidayHours.toFixed(1)}h` : "—"}
                </div>
                <div className="modal-bh-label">Holiday Hours</div>
              </div>
              <div className="modal-bh-stat">
                <div className="modal-bh-value">{record.maxConsecutiveOutsideHours.toFixed(1)}h</div>
                <div className="modal-bh-label">Max Consecutive</div>
              </div>
              <div className="modal-bh-stat">
                <div className="modal-bh-value">{record.uniquePeriodsOutside}</div>
                <div className="modal-bh-label">Unique Periods</div>
              </div>
            </div>
          </div>
        )}

        {/* Incidents list */}
        <div className="modal-body">
          <div className="modal-col" style={{ gridColumn: "1 / -1" }}>
            <div className="modal-col-header">
              Incidents Responded
              <span className="modal-col-count">{sortedIncidents.length}</span>
              {record.highUrgencyCount > 0 && (
                <span className="urgency-chip high" style={{ marginLeft: 6, fontWeight: 400 }}>
                  {record.highUrgencyCount} high
                </span>
              )}
            </div>
            <div className="modal-col-scroll">
              {sortedIncidents.length === 0 ? (
                <div className="detail-empty">No incidents during this period.</div>
              ) : (
                sortedIncidents.map((inc) => (
                  <div key={inc.id} className="incident-row">
                    <div className="incident-row-header">
                      <span className="incident-row-title">
                        #{inc.incidentNumber} {inc.title}
                      </span>
                      <span className={`urgency-chip ${inc.urgency}`}>{inc.urgency}</span>
                    </div>
                    <div className="incident-row-meta">
                      <span>{formatDateTime(inc.createdAt)}</span>
                      {inc.durationHours > 0 && (
                        <span>· {inc.durationHours.toFixed(1)}h</span>
                      )}
                      {inc.serviceName && <span>· {inc.serviceName}</span>}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
