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
  const [isTriaging, setIsTriaging] = useState(false);
  const [isTriagingAdvance, setIsTriagingAdvance] = useState(false);

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

  /**
   * Triage incident with generic AI
   */
  const handleTriageIt = async () => {
    if (!details) return;

    setIsTriaging(true);
    try {
      const incident = details.incident;
      const alerts = details.alerts || [];
      const notes = details.notes || [];
      const runbookUrls = parseRunbookUrls(incident);

      // Format incident details as markdown for the model
      const markdown = `# PagerDuty Incident #${incident.incident_number}

## Summary
**Status:** ${incident.status}
**Urgency:** ${incident.urgency}
**Priority:** ${incident.priority?.summary || 'None'}
**Service:** ${incident.service?.summary || 'Unknown'}
**Assigned to:** ${incident.assignments?.[0]?.assignee?.summary || 'Unassigned'}
**Created:** ${incident.created_at}

## Description
${incident.title}

${incident.description || 'No description provided'}

## Full Incident Payload
\`\`\`json
${JSON.stringify(incident, null, 2)}
\`\`\`

## Alerts (${alerts.length})
${alerts.map((alert: any, idx: number) => `
### Alert ${idx + 1}: ${alert.summary}
- **Status:** ${alert.status}
- **Severity:** ${alert.severity || 'unknown'}
- **Created:** ${alert.created_at}

**Full Alert Payload:**
\`\`\`json
${JSON.stringify(alert, null, 2)}
\`\`\`
`).join('\n')}

## Recent Notes (${notes.length})
${notes.slice(0, 5).map((note: any) => `
- **${note.user?.summary || 'Unknown'}** (${note.created_at}): ${note.content}
`).join('\n')}

## Runbook Links
${runbookUrls.length > 0 ? runbookUrls.map(url => `- ${url}`).join('\n') : 'No runbook links found'}

---
**Action needed:** Please help investigate and resolve this incident. Focus on the error details in the alert payloads and suggest next steps based on the incident history. Pay special attention to any file paths, stack traces, or error messages in the alert bodies.`;

      // Send to model context
      await app.updateModelContext({
        content: [
          {
            type: "text",
            text: markdown,
          },
        ],
      });

      console.log("[IncidentDetailsModal] Incident context sent to model");

      // Send a trigger message to activate the model's response
      await app.sendMessage({
        role: "user",
        content: [
          {
            type: "text",
            text: "I've handed over this PagerDuty incident to you. Please analyze the error details in the alerts and suggest next steps for resolution. If you see file paths or error stack traces, help me navigate to the relevant code.",
          },
        ],
      });

      console.log("[IncidentDetailsModal] Incident triaged successfully");

      // Close modal after successful triage
      onClose();
    } catch (err) {
      console.error("[IncidentDetailsModal] Failed to triage incident:", err);
      setError("Failed to triage incident. Please try again.");
    } finally {
      setIsTriaging(false);
    }
  };

  /**
   * Triage incident using PagerDuty Advance MCP server
   */
  const handleTriageWithAdvance = async () => {
    if (!details) return;

    setIsTriagingAdvance(true);
    try {
      const incident = details.incident;
      const alerts = details.alerts || [];
      const notes = details.notes || [];
      const runbookUrls = parseRunbookUrls(incident);

      // Format incident details as markdown for the model
      const markdown = `# PagerDuty Incident #${incident.incident_number}

## Summary
**Status:** ${incident.status}
**Urgency:** ${incident.urgency}
**Priority:** ${incident.priority?.summary || 'None'}
**Service:** ${incident.service?.summary || 'Unknown'}
**Assigned to:** ${incident.assignments?.[0]?.assignee?.summary || 'Unassigned'}
**Created:** ${incident.created_at}

## Description
${incident.title}

${incident.description || 'No description provided'}

## Full Incident Payload
\`\`\`json
${JSON.stringify(incident, null, 2)}
\`\`\`

## Alerts (${alerts.length})
${alerts.map((alert: any, idx: number) => `
### Alert ${idx + 1}: ${alert.summary}
- **Status:** ${alert.status}
- **Severity:** ${alert.severity || 'unknown'}
- **Created:** ${alert.created_at}

**Full Alert Payload:**
\`\`\`json
${JSON.stringify(alert, null, 2)}
\`\`\`
`).join('\n')}

## Recent Notes (${notes.length})
${notes.slice(0, 5).map((note: any) => `
- **${note.user?.summary || 'Unknown'}** (${note.created_at}): ${note.content}
`).join('\n')}

## Runbook Links
${runbookUrls.length > 0 ? runbookUrls.map(url => `- ${url}`).join('\n') : 'No runbook links found'}

---
**Action needed:** Please triage this incident using PagerDuty Advance. Check if the PagerDuty Advance MCP server is available and use its tools to analyze and triage this incident. The incident ID is: ${incident.id}`;

      // Send to model context
      await app.updateModelContext({
        content: [
          {
            type: "text",
            text: markdown,
          },
        ],
      });

      console.log("[IncidentDetailsModal] Incident context sent to model for PD Advance triage");

      // Send a trigger message to activate PD Advance triage
      await app.sendMessage({
        role: "user",
        content: [
          {
            type: "text",
            text: `Please triage this PagerDuty incident using the PagerDuty Advance MCP server. Use the sre_agent_tool from the pagerduty-advance-mcp server with the following incident ID: ${incident.id}

This tool requires the incident_id parameter. Please run it to get SRE agent analysis and recommendations for this incident.`,
          },
        ],
      });

      console.log("[IncidentDetailsModal] Incident sent for PD Advance triage successfully");

      // Close modal after successful triage
      onClose();
    } catch (err) {
      console.error("[IncidentDetailsModal] Failed to triage with PD Advance:", err);
      setError("Failed to triage with PD Advance. Please try again.");
    } finally {
      setIsTriagingAdvance(false);
    }
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
          <button
            className="btn-primary"
            onClick={handleTriageIt}
            disabled={isTriaging}
          >
            {isTriaging ? "⏳" : "🤖"} Triage Locally
          </button>
          <button
            className="btn-primary"
            onClick={handleTriageWithAdvance}
            disabled={isTriagingAdvance}
            style={{
              background: isTriagingAdvance ? "#999" : "#048a24",
              color: "#fff",
              border: "none",
            }}
          >
            {isTriagingAdvance ? "⏳ Triaging..." : "✨ Triage with SRE Agent"}
          </button>
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
