/**
 * Incident Command Center - React Client
 *
 * Real-time incident management dashboard with deep incident details
 */

import type { App, McpUiHostContext } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchIncidents, acknowledgeIncident, resolveIncident, addIncidentNote, fetchIncidentDetails } from "./api";
import { IncidentDetailsModal } from "./components/IncidentDetailsModal";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { ActionsDropdown } from "./components/ActionsDropdown";
import { EscalationModal } from "./components/EscalationModal";
import { PriorityModal } from "./components/PriorityModal";
import { WorkflowModal } from "./components/WorkflowModal";

// Types
interface Incident {
  id: string;
  incident_number: number;
  title: string;
  status: "triggered" | "acknowledged" | "resolved";
  urgency: "high" | "low";
  created_at: string;
  service: {
    id: string;
    summary: string;
  };
  priority?: {
    id: string;
    summary: string;
    name: string;
  };
  assignments?: Array<{
    assignee: {
      id: string;
      summary: string;
    };
  }>;
  alert_counts?: {
    triggered: number;
    resolved: number;
  };
}

interface DashboardData {
  incidents: Incident[];
  filters: {
    status: string[];
    urgency: string[];
    auto_refresh: boolean;
  };
  metadata: {
    timestamp: string;
    total_count: number;
  };
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

// Main App Component
function IncidentCommandCenter() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [detailsModalIncidentId, setDetailsModalIncidentId] = useState<string | null>(null);
  const [hostContext, setHostContext] = useState<McpUiHostContext | undefined>();
  const [error, setError] = useState<string | null>(null);

  // Debug logging
  console.log("[IncidentCommandCenter] Component mounted");

  const { app, error: connectionError } = useApp({
    appInfo: { name: "Incident Command Center", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      console.log("[IncidentCommandCenter] App created successfully", app);

      // Note: We don't need ontoolresult handler since we call tools directly
      // and get responses synchronously via callServerTool()

      app.onerror = (err) => {
        console.error("[IncidentCommandCenter] App error:", err);
        setError(err.message);
      };

      app.onhostcontextchanged = (params) => {
        console.log("[IncidentCommandCenter] Host context changed:", params);
        setHostContext((prev) => ({ ...prev, ...params }));

        // Update theme if it changed
        if (params.theme) {
          console.log("[IncidentCommandCenter] Theme changed to:", params.theme);
          document.documentElement.setAttribute('data-theme', params.theme);
        }
      };
    },
  });

  // Get initial host context and handle container dimensions
  useEffect(() => {
    if (app) {
      const context = app.getHostContext();
      setHostContext(context);

      // Apply theme from VS Code
      const theme = context?.theme || 'light';
      console.log("[IncidentCommandCenter] Theme from VS Code:", theme);
      document.documentElement.setAttribute('data-theme', theme);

      // Handle container dimensions per MCP Apps spec
      const dims = context?.containerDimensions;
      console.log("[IncidentCommandCenter] Container dimensions:", dims);

      const root = document.documentElement;
      
      // Always use full viewport height to ensure internal scrolling works
      root.style.height = "100vh";
      root.style.minHeight = "100vh";
      document.body.style.height = "100vh";
      console.log("[IncidentCommandCenter] Using full viewport height");

      if (dims) {
        // Handle width constraints if present
        if ("width" in dims && dims.width) {
          root.style.width = "100vw";
        } else if ("maxWidth" in dims && dims.maxWidth) {
          root.style.maxWidth = `${dims.maxWidth}px`;
          root.style.margin = "0 auto"; // Center it
        }
      } else {
        // No dimensions specified, use full viewport
        console.log("[IncidentCommandCenter] No container dimensions, using full viewport");
        document.documentElement.style.minHeight = "600px";
      }

      // Request reasonable minimum height for dashboard (even with 1 incident)
      console.log("[IncidentCommandCenter] Requesting minimum height of 500px");
      app.notification({
        method: "ui/notifications/size-changed",
        params: { height: 500 }
      }).catch((err: Error) => {
        console.log("[IncidentCommandCenter] Size change not supported:", err.message);
      });
    }
  }, [app]);

  // Load initial data
  const loadData = useCallback(async () => {
    if (!app) {
      console.log("[IncidentCommandCenter] loadData called but app not ready");
      return;
    }

    console.log("[IncidentCommandCenter] Loading incidents...");
    try {
      const newData = await fetchIncidents(app, {
        status: ["triggered", "acknowledged"],
        urgency: [],
        auto_refresh: true,
      });
      console.log("[IncidentCommandCenter] Fetched data:", newData);
      if (newData) {
        setData(newData);
      }
    } catch (err) {
      console.error("[IncidentCommandCenter] Failed to load incidents:", err);
      setError(`Failed to load incidents: ${err}`);
    }
  }, [app]);

  useEffect(() => {
    console.log("[IncidentCommandCenter] loadData effect triggered, app:", !!app);
    loadData();
  }, [loadData]);

  // Auto-refresh
  useEffect(() => {
    if (!app || !data?.filters.auto_refresh) return;

    const interval = setInterval(async () => {
      try {
        const newData = await fetchIncidents(app, data.filters);
        if (newData) {
          setData(newData);
        }
      } catch (err) {
        console.error("Auto-refresh failed:", err);
      }
    }, 10000); // 10 seconds

    return () => clearInterval(interval);
  }, [app, data?.filters]);

  console.log("[IncidentCommandCenter] Render state:", {
    hasApp: !!app,
    hasData: !!data,
    hasError: !!error,
    connectionError: connectionError?.message,
    incidentCount: data?.incidents?.length
  });

  if (connectionError) {
    console.error("[IncidentCommandCenter] Rendering connection error");
    return (
      <div className="error-container" style={{
        padding: "20px",
        background: "#fee",
        border: "2px solid red",
        margin: "10px"
      }}>
        <h2>❌ Connection Error</h2>
        <p>{connectionError.message}</p>
        <pre style={{ fontSize: "10px", overflow: "auto" }}>{JSON.stringify(connectionError, null, 2)}</pre>
      </div>
    );
  }

  if (!app) {
    console.log("[IncidentCommandCenter] Rendering loading state");
    return (
      <div className="loading-container" style={{
        padding: "40px",
        textAlign: "center",
        background: "#f0f0f0",
        margin: "10px"
      }}>
        <div className="spinner"></div>
        <h2>⏳ Connecting to Incident Command Center...</h2>
        <p style={{ fontSize: "12px", color: "#666" }}>Initializing MCP App connection...</p>
      </div>
    );
  }

  console.log("[IncidentCommandCenter] Rendering dashboard");
  return (
    <div style={{ height: "100%", width: "100%", background: "#fff" }}>
      <IncidentDashboard
        app={app}
        data={data}
        onIncidentClick={setDetailsModalIncidentId}
        onRefresh={loadData}
        hostContext={hostContext}
        error={error}
      />
      {detailsModalIncidentId && (
        <IncidentDetailsModal
          app={app}
          incidentId={detailsModalIncidentId}
          onClose={() => setDetailsModalIncidentId(null)}
          onRefresh={loadData}
        />
      )}
    </div>
  );
}

// Dashboard Component
interface IncidentDashboardProps {
  app: App;
  data: DashboardData | null;
  onIncidentClick: (id: string) => void;
  onRefresh: () => void;
  hostContext?: McpUiHostContext;
  error: string | null;
}

function IncidentDashboard({
  app,
  data,
  onIncidentClick,
  onRefresh,
  hostContext,
  error,
}: IncidentDashboardProps) {
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  console.log("[IncidentDashboard] Rendering with data:", data);

  const handleQuickAction = useCallback(
    async (incidentId: string, action: "acknowledge" | "resolve") => {
      setActionLoading(incidentId);

      try {
        if (action === "acknowledge") {
          await acknowledgeIncident(app, incidentId);
        } else {
          await resolveIncident(app, incidentId);
        }

        // Refresh dashboard
        onRefresh();
      } catch (err) {
        console.error("[IncidentDashboard] Action failed:", err);
      } finally {
        setActionLoading(null);
      }
    },
    [app, onRefresh],
  );

  if (!data) {
    console.log("[IncidentDashboard] No data, showing loading state");
    return (
      <div className="loading-container" style={{
        padding: "40px",
        textAlign: "center",
        background: "#f9f9f9",
        margin: "20px"
      }}>
        <div className="spinner"></div>
        <h3>⏳ Loading incidents...</h3>
        <p style={{ fontSize: "12px", color: "#666" }}>Fetching data from PagerDuty API...</p>
      </div>
    );
  }

  console.log("[IncidentDashboard] Rendering dashboard with", data.incidents.length, "incidents");

  return (
    <main
      className="dashboard"
      style={{
        paddingTop: hostContext?.safeAreaInsets?.top,
        paddingRight: hostContext?.safeAreaInsets?.right,
        paddingBottom: hostContext?.safeAreaInsets?.bottom,
        paddingLeft: hostContext?.safeAreaInsets?.left,
      }}
    >
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-title-row">
          <PagerDutyLogo size={36} />
          <h1>Incident Command Center</h1>
        </div>
        <div className="header-meta">
          <span className="incident-count">
            {data.incidents.length} Active Incidents
          </span>
          <span className="last-update">
            Updated: {formatTimestamp(data.metadata.timestamp)}
          </span>
          {data.filters.auto_refresh && (
            <span className="auto-refresh">🔄 Auto-refresh ON</span>
          )}
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Incident List */}
        <div className="incident-list">
          {data.incidents.length === 0 ? (
            <div className="empty-state">
              <p>🎉 No active incidents</p>
              <p className="empty-subtext">All systems operational</p>
            </div>
          ) : (
            data.incidents.map((incident) => (
              <IncidentCard
                key={incident.id}
                incident={incident}
                onClick={() => onIncidentClick(incident.id)}
                onAcknowledge={(e) => {
                  e.stopPropagation();
                  handleQuickAction(incident.id, "acknowledge");
                }}
                onResolve={(e) => {
                  e.stopPropagation();
                  handleQuickAction(incident.id, "resolve");
                }}
                isLoading={actionLoading === incident.id}
                app={app}
                onRefresh={onRefresh}
              />
            ))
          )}
        </div>
      </div>
    </main>
  );
}

// Incident Card Component
interface IncidentCardProps {
  incident: Incident;
  onClick: () => void;
  onAcknowledge: (e: React.MouseEvent) => void;
  onResolve: (e: React.MouseEvent) => void;
  isLoading: boolean;
  app: App;
  onRefresh: () => void;
}

function IncidentCard({
  incident,
  onClick,
  onAcknowledge,
  onResolve,
  isLoading,
  app,
  onRefresh,
}: IncidentCardProps) {
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [showPriorityModal, setShowPriorityModal] = useState(false);
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);
  const [isTriaging, setIsTriaging] = useState(false);
  const [isTriagingAdvance, setIsTriagingAdvance] = useState(false);

  /**
   * Parse runbook URLs from incident description or metadata
   */
  const parseRunbookUrls = (incident: any): string[] => {
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
  };

  /**
   * Triage incident with generic AI
   */
  const handleTriageIt = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsTriaging(true);

    try {
      // Fetch full incident details
      const details = await fetchIncidentDetails(app, incident.id);
      if (!details) {
        throw new Error("Failed to fetch incident details");
      }

      const fullIncident = details.incident;
      const alerts = details.alerts || [];
      const notes = details.notes || [];
      const runbookUrls = parseRunbookUrls(fullIncident);

      // Format incident details as markdown for the model
      const markdown = `# PagerDuty Incident #${fullIncident.incident_number}

## Summary
**Status:** ${fullIncident.status}
**Urgency:** ${fullIncident.urgency}
**Priority:** ${fullIncident.priority?.summary || 'None'}
**Service:** ${fullIncident.service?.summary || 'Unknown'}
**Assigned to:** ${fullIncident.assignments?.[0]?.assignee?.summary || 'Unassigned'}
**Created:** ${fullIncident.created_at}

## Description
${fullIncident.title}

${fullIncident.description || 'No description provided'}

## Full Incident Payload
\`\`\`json
${JSON.stringify(fullIncident, null, 2)}
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

      console.log("[IncidentCard] Incident context sent to model");

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

      console.log("[IncidentCard] Incident triaged successfully");
    } catch (err) {
      console.error("[IncidentCard] Failed to triage incident:", err);
      alert("Failed to triage incident. Please try again.");
    } finally {
      setIsTriaging(false);
    }
  };

  /**
   * Triage incident using PagerDuty Advance MCP server
   */
  const handleTriageWithAdvance = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsTriagingAdvance(true);

    try {
      // Fetch full incident details
      const details = await fetchIncidentDetails(app, incident.id);
      if (!details) {
        throw new Error("Failed to fetch incident details");
      }

      const fullIncident = details.incident;
      const alerts = details.alerts || [];
      const notes = details.notes || [];
      const runbookUrls = parseRunbookUrls(fullIncident);

      // Format incident details as markdown for the model
      const markdown = `# PagerDuty Incident #${fullIncident.incident_number}

## Summary
**Status:** ${fullIncident.status}
**Urgency:** ${fullIncident.urgency}
**Priority:** ${fullIncident.priority?.summary || 'None'}
**Service:** ${fullIncident.service?.summary || 'Unknown'}
**Assigned to:** ${fullIncident.assignments?.[0]?.assignee?.summary || 'Unassigned'}
**Created:** ${fullIncident.created_at}

## Description
${fullIncident.title}

${fullIncident.description || 'No description provided'}

## Full Incident Payload
\`\`\`json
${JSON.stringify(fullIncident, null, 2)}
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
**Action needed:** Please triage this incident using PagerDuty Advance. Check if the PagerDuty Advance MCP server is available and use its tools to analyze and triage this incident. The incident ID is: ${fullIncident.id}`;

      // Send to model context
      await app.updateModelContext({
        content: [
          {
            type: "text",
            text: markdown,
          },
        ],
      });

      console.log("[IncidentCard] Incident context sent to model for PD Advance triage");

      // Send a trigger message to activate PD Advance triage
      await app.sendMessage({
        role: "user",
        content: [
          {
            type: "text",
            text: `Please triage this PagerDuty incident using the PagerDuty Advance MCP server. Use the sre_agent_tool from the pagerduty-advance-mcp server with the following incident ID: ${fullIncident.id}

This tool requires the incident_id parameter. Please run it to get SRE agent analysis and recommendations for this incident.`,
          },
        ],
      });

      console.log("[IncidentCard] Incident sent for PD Advance triage successfully");
    } catch (err) {
      console.error("[IncidentCard] Failed to triage with PD Advance:", err);
      alert("Failed to triage with PD Advance. Please try again.");
    } finally {
      setIsTriagingAdvance(false);
    }
  };
  return (
    <div
      className={`incident-card urgency-${incident.urgency}`}
      onClick={onClick}
      style={{ cursor: "pointer" }}
    >
      {/* Header */}
      <div className="incident-header">
        <span className="incident-number">#{incident.incident_number}</span>
        <span className={`status-badge status-${incident.status}`}>
          {incident.status}
        </span>
        <span className={`urgency-badge urgency-${incident.urgency}`}>
          {incident.urgency} urgency
        </span>
        <span className={`priority-badge ${incident.priority ? '' : 'no-priority'}`}>
          {incident.priority ? incident.priority.summary : 'No Priority'}
        </span>
      </div>

      {/* Title */}
      <h3 className="incident-title">{incident.title}</h3>

      {/* Meta Info */}
      <div className="incident-meta">
        <span className="service-name">📦 {incident.service.summary}</span>
        {incident.assignments?.[0] && (
          <span className="assignee">👤 {incident.assignments[0].assignee.summary}</span>
        )}
        <span className="created-time">🕐 {formatTimestamp(incident.created_at)}</span>
      </div>

      {/* Alert Counts */}
      {incident.alert_counts && (
        <div className="alert-counts">
          <span className="alert-count triggered">
            🔔 {incident.alert_counts.triggered} triggered
          </span>
          <span className="alert-count resolved">
            ✅ {incident.alert_counts.resolved} resolved
          </span>
        </div>
      )}

      {/* Slack-style Action Buttons */}
      <div className="incident-actions">
        <button className="action-btn details" onClick={(e) => { e.stopPropagation(); onClick(); }}>
          🔍 Details
        </button>
        {incident.status === "triggered" && (
          <button
            className="action-btn acknowledge"
            onClick={onAcknowledge}
            disabled={isLoading}
          >
            {isLoading ? "⏳" : "✓"} Acknowledge
          </button>
        )}
        {incident.status !== "resolved" && (
          <button
            className="action-btn resolve"
            onClick={onResolve}
            disabled={isLoading}
          >
            {isLoading ? "⏳" : "✓"} Resolve
          </button>
        )}
        <button
          className="action-btn triage"
          onClick={handleTriageIt}
          disabled={isLoading || isTriaging}
        >
          {isTriaging ? "⏳" : "🤖"} Triage Locally
        </button>
        <button
          className="action-btn triage-advance"
          onClick={handleTriageWithAdvance}
          disabled={isLoading || isTriagingAdvance}
          style={{
            background: isTriagingAdvance ? "#999" : "#048a24",
            color: "#fff",
            border: "none",
          }}
        >
          {isTriagingAdvance ? "⏳ Triaging..." : "✨ Triage with SRE Agent"}
        </button>
        <ActionsDropdown
          disabled={isLoading}
          actions={[
            {
              label: "Add Note",
              icon: "📝",
              onClick: () => {
                setShowNoteModal(true);
              },
            },
            {
              label: "Run Workflow",
              icon: "⚡",
              onClick: () => {
                setShowWorkflowModal(true);
              },
            },
            {
              label: "Change Priority",
              icon: "🎯",
              onClick: () => {
                setShowPriorityModal(true);
              },
            },
            {
              label: "Escalate",
              icon: "⬆️",
              onClick: () => {
                setShowEscalationModal(true);
              },
            },
            {
              label: "Reassign",
              icon: "👤",
              onClick: () => {
                alert("Reassign - To be implemented");
              },
            },
          ]}
        />
      </div>

      {/* Quick Note Modal */}
      {showNoteModal && (
        <div className="quick-note-modal" onClick={(e) => e.stopPropagation()}>
          <div className="quick-note-content" onClick={(e) => e.stopPropagation()}>
            <h4>Add Note to Incident #{incident.incident_number}</h4>
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Enter your note..."
              rows={3}
            />
            <div className="quick-note-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowNoteModal(false);
                  setNoteText("");
                }}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                disabled={!noteText.trim() || isSubmittingNote}
                onClick={async () => {
                  if (!noteText.trim()) return;
                  setIsSubmittingNote(true);
                  try {
                    await addIncidentNote(app, incident.id, noteText);
                    setShowNoteModal(false);
                    setNoteText("");
                    onRefresh();
                  } catch (err) {
                    console.error("Failed to add note:", err);
                    alert("Failed to add note");
                  } finally {
                    setIsSubmittingNote(false);
                  }
                }}
              >
                {isSubmittingNote ? "Adding..." : "Add Note"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Escalation Modal */}
      {showEscalationModal && (
        <div onClick={(e) => e.stopPropagation()}>
          <EscalationModal
            app={app}
            incident={incident}
            onClose={() => setShowEscalationModal(false)}
            onEscalated={() => {
              setShowEscalationModal(false);
              onRefresh();
            }}
          />
        </div>
      )}

      {/* Priority Change Modal */}
      {showPriorityModal && (
        <div onClick={(e) => e.stopPropagation()}>
          <PriorityModal
            app={app}
            incident={incident}
            onClose={() => setShowPriorityModal(false)}
            onChanged={() => {
              setShowPriorityModal(false);
              onRefresh();
            }}
          />
        </div>
      )}

      {/* Workflow Modal */}
      {showWorkflowModal && (
        <div onClick={(e) => e.stopPropagation()}>
          <WorkflowModal
            app={app}
            incident={incident}
            onClose={() => setShowWorkflowModal(false)}
            onStarted={() => {
              setShowWorkflowModal(false);
              onRefresh();
            }}
          />
        </div>
      )}
    </div>
  );
}

// Render
const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <IncidentCommandCenter />
    </StrictMode>,
  );
} else {
  console.error("Failed to find root element");
}
