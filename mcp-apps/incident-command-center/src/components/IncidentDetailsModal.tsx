/**
 * IncidentDetailsModal - Comprehensive incident details view
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import { useState, useEffect } from "react";
import { fetchIncidentDetails } from "../api";
import { Timeline } from "./Timeline";
import { AlertInspector } from "./AlertInspector";

interface IncidentDetailsModalProps {
  app: App;
  incidentId: string;
  onClose: () => void;
  onRefresh: () => void;
}

/**
 * Parse runbook URLs from incident description or metadata
 */
function parseRunbookUrls(incident: any): string[] {
  const urls: string[] = [];
  const urlRegex = /(https?:\/\/[^\s]+)/g;

  // Check description
  if (incident.description) {
    const matches = incident.description.match(urlRegex);
    if (matches) {
      urls.push(...matches.filter((url: string) =>
        url.includes("runbook") || url.includes("playbook") || url.includes("wiki")
      ));
    }
  }

  // Check service metadata
  if (incident.service?.description) {
    const matches = incident.service.description.match(urlRegex);
    if (matches) {
      urls.push(...matches.filter((url: string) =>
        url.includes("runbook") || url.includes("playbook") || url.includes("wiki")
      ));
    }
  }

  return [...new Set(urls)]; // Deduplicate
}

export function IncidentDetailsModal({
  app,
  incidentId,
  onClose,
  onRefresh,
}: IncidentDetailsModalProps) {
  const [details, setDetails] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"timeline" | "alerts">("timeline");

  // Fetch incident details
  const loadDetails = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchIncidentDetails(app, incidentId);
      if (data) {
        setDetails(data);
      } else {
        setError("Failed to load incident details");
      }
    } catch (err) {
      setError("Failed to load incident details");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Request more space when modal opens
  useEffect(() => {
    console.log("[Modal] Requesting larger container size (700px) for modal");
    app.notification({
      method: "ui/notifications/size-changed",
      params: { height: 700 }
    }).catch((err: Error) => {
      console.log("[Modal] Size change notification not supported or failed:", err.message);
    });

    // Restore original size when modal closes
    return () => {
      console.log("[Modal] Restoring original container size");
      app.notification({
        method: "ui/notifications/size-changed",
        params: { height: 500 }
      }).catch(() => {
        // Ignore errors on cleanup
      });
    };
  }, [app]);

  useEffect(() => {
    loadDetails();
  }, [incidentId, app]);

  const handleRefresh = () => {
    loadDetails();
    onRefresh(); // Also refresh parent
  };

  if (isLoading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-loading">
            <div className="spinner"></div>
            <p>Loading incident details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-error">
            <h3>Error</h3>
            <p>{error || "Failed to load details"}</p>
            <button onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    );
  }

  const runbookUrls = parseRunbookUrls(details.incident);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content incident-details-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title">
            <h2>🔍 Incident #{details.incident.incident_number}</h2>
            <span className={`status-badge status-${details.incident.status}`}>
              {details.incident.status}
            </span>
          </div>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Incident summary */}
        <div className="modal-summary">
          <h3>{details.incident.title}</h3>
          <div className="summary-meta">
            <span>📦 {details.incident.service?.summary}</span>
            {details.incident.assignments?.[0] && (
              <span>👤 {details.incident.assignments[0].assignee.summary}</span>
            )}
            <span className={`urgency-badge urgency-${details.incident.urgency}`}>
              {details.incident.urgency} urgency
            </span>
          </div>
        </div>

        {/* Runbook links */}
        {runbookUrls.length > 0 && (
          <div className="runbook-section">
            <h4>📚 Runbooks</h4>
            <div className="runbook-links">
              {runbookUrls.map((url, idx) => (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="runbook-link"
                >
                  {url}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="modal-tabs">
          <button
            className={`tab-button ${activeTab === "timeline" ? "active" : ""}`}
            onClick={() => setActiveTab("timeline")}
          >
            Timeline
          </button>
          <button
            className={`tab-button ${activeTab === "alerts" ? "active" : ""}`}
            onClick={() => setActiveTab("alerts")}
          >
            Alerts ({details.alerts.length})
          </button>
        </div>

        {/* Tab content */}
        <div className="modal-body">
          {activeTab === "timeline" && (
            <div className="tab-content">
              <Timeline
                notes={[]}
                alerts={details.alerts}
                changes={details.changes}
              />
            </div>
          )}

          {activeTab === "alerts" && (
            <div className="tab-content">
              <AlertInspector alerts={details.alerts} />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn-secondary" onClick={handleRefresh}>
            🔄 Refresh
          </button>
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
