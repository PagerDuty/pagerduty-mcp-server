/**
 * Standalone Escalation Modal - Can be triggered from dropdown
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import { EscalationPanel } from "./EscalationPanel";

interface EscalationModalProps {
  app: App;
  incident: any;
  onClose: () => void;
  onEscalated: () => void;
}

export function EscalationModal({ app, incident, onClose, onEscalated }: EscalationModalProps) {
  const handleEscalated = () => {
    onEscalated();
    onClose();
  };

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="modal-content escalation-modal-content">
        <div className="modal-header">
          <div className="modal-title">
            <h2>Escalate Incident #{incident.incident_number}</h2>
          </div>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <div className="modal-summary">
            <h3>{incident.title}</h3>
            <div className="summary-meta">
              <span>Service: {incident.service.summary}</span>
              <span className={`status-badge status-${incident.status}`}>
                {incident.status}
              </span>
              <span className={`urgency-badge urgency-${incident.urgency}`}>
                {incident.urgency}
              </span>
            </div>
          </div>
          <div style={{ padding: "20px 24px" }}>
            <EscalationPanel
              app={app}
              incident={incident}
              onEscalated={handleEscalated}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
