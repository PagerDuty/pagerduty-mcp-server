/**
 * AlertInspector - Alert drill-down and details view
 */

import { useState } from "react";

interface Alert {
  id: string;
  summary: string;
  created_at: string;
  status: string;
  severity: string;
  body?: {
    type?: string;
    details?: any;
  };
}

interface AlertInspectorProps {
  alerts: Alert[];
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString();
}

export function AlertInspector({ alerts }: AlertInspectorProps) {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  return (
    <div className="alert-inspector">
      <h4>🔔 Alerts ({alerts.length})</h4>

      <div className="alert-inspector-content">
        {/* Alert list */}
        <div className="alert-list">
          {alerts.length === 0 ? (
            <p className="empty-alerts">No alerts found</p>
          ) : (
            alerts.map((alert) => (
              <div
                key={alert.id}
                className={`alert-card ${selectedAlert?.id === alert.id ? "selected" : ""}`}
                onClick={() => setSelectedAlert(alert)}
              >
                <div className="alert-header">
                  <span className={`alert-status status-${alert.status}`}>
                    {alert.status}
                  </span>
                  {alert.severity && (
                    <span className={`alert-severity severity-${alert.severity.toLowerCase()}`}>
                      {alert.severity}
                    </span>
                  )}
                </div>
                <p className="alert-summary">{alert.summary}</p>
                <span className="alert-time">{formatTimestamp(alert.created_at)}</span>
              </div>
            ))
          )}
        </div>

        {/* Alert details */}
        {selectedAlert && (
          <div className="alert-details">
            <div className="alert-details-header">
              <h5>Alert Details</h5>
              <button className="close-btn" onClick={() => setSelectedAlert(null)}>
                ✕
              </button>
            </div>

            <div className="alert-details-body">
              <div className="alert-detail-section">
                <strong>ID:</strong> {selectedAlert.id}
              </div>
              <div className="alert-detail-section">
                <strong>Status:</strong> {selectedAlert.status}
              </div>
              <div className="alert-detail-section">
                <strong>Created:</strong> {formatTimestamp(selectedAlert.created_at)}
              </div>
              {selectedAlert.severity && (
                <div className="alert-detail-section">
                  <strong>Severity:</strong> {selectedAlert.severity}
                </div>
              )}
              <div className="alert-detail-section">
                <strong>Summary:</strong>
                <p>{selectedAlert.summary}</p>
              </div>

              {/* Alert body/details */}
              {selectedAlert.body && (
                <div className="alert-detail-section">
                  <strong>Raw Alert Data:</strong>
                  <pre className="alert-body">
                    {JSON.stringify(selectedAlert.body, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
