/**
 * AlertInspector - Alert drill-down and details view
 */

import { useState } from "react";

/** Syntax-highlighted JSON viewer */
function JsonViewer({ data }: { data: any }) {
  const escaped = JSON.stringify(data, null, 2)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const highlighted = escaped.replace(
    /("(\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = "json-number";
      if (/^"|'/.test(match)) {
        cls = /:$/.test(match) ? "json-key" : "json-string";
      } else if (/true|false/.test(match)) {
        cls = "json-boolean";
      } else if (/null/.test(match)) {
        cls = "json-null";
      }
      return `<span class="${cls}">${match}</span>`;
    }
  );

  return (
    <pre
      className="json-viewer"
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: highlighted }}
    />
  );
}

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
              <JsonViewer data={selectedAlert} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
