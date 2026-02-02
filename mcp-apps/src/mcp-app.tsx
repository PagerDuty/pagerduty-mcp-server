/**
 * PagerDuty Incident Dashboard
 *
 * Interactive dashboard with real-time incident trends, service health, and urgency distribution.
 */
import type { App, McpUiHostContext } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import "./global.css";

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Types matching server schemas
interface IncidentDashboardData {
  summary: {
    total_incidents: number;
    active_incidents: number;
    resolved_today: number;
    avg_resolution_time_minutes: number | null;
  };
  timeline: Array<{
    timestamp: string;
    triggered: number;
    acknowledged: number;
    resolved: number;
    total: number;
  }>;
  service_health: Array<{
    service_id: string;
    service_name: string;
    incident_count: number;
    high_urgency_count: number;
    low_urgency_count: number;
    avg_resolution_time_minutes: number | null;
    status: "healthy" | "warning" | "critical";
  }>;
  urgency_distribution: {
    high: number;
    low: number;
    total: number;
    high_percent: number;
    low_percent: number;
  };
  time_range: {
    start: string;
    end: string;
    label: string;
  };
  generated_at: string;
}

interface IncidentStats {
  timestamp: string;
  active_incidents: number;
  triggered_count: number;
  acknowledged_count: number;
  high_urgency_count: number;
  low_urgency_count: number;
  recent_incidents: Array<{
    id: string;
    incident_number: number;
    title: string;
    status: "triggered" | "acknowledged" | "resolved";
    urgency: "high" | "low";
    service_name: string;
    created_at: string;
  }>;
}

function extractDashboardData(toolResult: any): IncidentDashboardData | null {
  // Try to get structured content first
  if (toolResult.structuredContent) {
    return toolResult.structuredContent as IncidentDashboardData;
  }
  return null;
}

function IncidentDashboardApp() {
  const [toolResult, setToolResult] = useState<any | null>(null);
  const [hostContext, setHostContext] = useState<McpUiHostContext | undefined>();

  const { app, error } = useApp({
    appInfo: { name: "PagerDuty Incident Dashboard", version: "0.1.0" },
    capabilities: {},
    onAppCreated: (app) => {
      app.onteardown = async () => {
        console.info("[Dashboard] App is being torn down");
        return {};
      };

      app.ontoolinput = async (input) => {
        console.info("[Dashboard] Received tool call input:", input);
      };

      app.ontoolresult = async (result) => {
        console.info("[Dashboard] Received tool call result:", result);
        setToolResult(result);
      };

      app.ontoolcancelled = (params) => {
        console.info("[Dashboard] Tool call cancelled:", params.reason);
      };

      app.onerror = (error) => {
        console.error("[Dashboard] Error:", error);
      };

      app.onhostcontextchanged = (params) => {
        setHostContext((prev) => ({ ...prev, ...params }));
      };
    },
  });

  useEffect(() => {
    if (app) {
      setHostContext(app.getHostContext());
    }
  }, [app]);

  if (error) {
    return (
      <div style={{ padding: "20px", color: "red" }}>
        <strong>ERROR:</strong> {error.message}
        <pre style={{ marginTop: "10px", fontSize: "12px" }}>{JSON.stringify(error, null, 2)}</pre>
      </div>
    );
  }

  if (!app) {
    return (
      <div style={{ padding: "20px" }}>
        <h2>🔄 Connecting to MCP...</h2>
        <p>Initializing dashboard application...</p>
      </div>
    );
  }

  return <IncidentDashboardInner app={app} toolResult={toolResult} hostContext={hostContext} />;
}

interface IncidentDashboardInnerProps {
  app: App;
  toolResult: any | null;
  hostContext?: McpUiHostContext;
}

function IncidentDashboardInner({
  app,
  toolResult,
  hostContext,
}: IncidentDashboardInnerProps) {
  const [currentStats, setCurrentStats] = useState<IncidentStats | null>(null);
  const [isPolling, setIsPolling] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  const timelineChartRef = useRef<HTMLCanvasElement>(null);
  const urgencyChartRef = useRef<HTMLCanvasElement>(null);
  const timelineChart = useRef<Chart | null>(null);
  const urgencyChart = useRef<Chart | null>(null);

  // Extract dashboard data from tool result
  const dashboardData = extractDashboardData(toolResult);

  // Show loading state if we don't have data yet
  if (!dashboardData) {
    return (
      <div style={{ padding: "20px" }}>
        <h2>⏳ Loading dashboard data...</h2>
        <p>App connected. Waiting for incident data...</p>
        <p style={{ fontSize: "12px", color: "#666", marginTop: "10px" }}>
          Tool result: {toolResult ? "Received, parsing..." : "Not yet received"}
        </p>
      </div>
    );
  }

  // Initialize charts when dashboard data is available
  useEffect(() => {
    if (!timelineChartRef.current || !urgencyChartRef.current || !dashboardData) return;

    const isDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const textColor = isDarkMode ? "#9ca3af" : "#374151";
    const gridColor = isDarkMode ? "#374151" : "#e5e7eb";

    // Timeline chart
    timelineChart.current = new Chart(timelineChartRef.current, {
      type: "line",
      data: {
        labels: dashboardData.timeline.map((d) => {
          const date = new Date(d.timestamp);
          return dashboardData.time_range.label === "24h"
            ? date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
            : date.toLocaleDateString([], { month: "short", day: "numeric" });
        }),
        datasets: [
          {
            label: "Triggered",
            data: dashboardData.timeline.map((d) => d.triggered),
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            fill: true,
            tension: 0.4,
          },
          {
            label: "Acknowledged",
            data: dashboardData.timeline.map((d) => d.acknowledged),
            borderColor: "#f59e0b",
            backgroundColor: "rgba(245, 158, 11, 0.1)",
            fill: true,
            tension: 0.4,
          },
          {
            label: "Resolved",
            data: dashboardData.timeline.map((d) => d.resolved),
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: { color: textColor },
          },
          title: {
            display: true,
            text: `Incident Timeline (${dashboardData.time_range.label})`,
            color: textColor,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: textColor },
            grid: { color: gridColor },
          },
          x: {
            ticks: { color: textColor },
            grid: { color: gridColor },
          },
        },
      },
    });

    // Urgency donut chart
    urgencyChart.current = new Chart(urgencyChartRef.current, {
      type: "doughnut",
      data: {
        labels: ["High Urgency", "Low Urgency"],
        datasets: [
          {
            data: [
              dashboardData.urgency_distribution.high,
              dashboardData.urgency_distribution.low,
            ],
            backgroundColor: ["#ef4444", "#f59e0b"],
            borderWidth: 2,
            borderColor: isDarkMode ? "#1f2937" : "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "60%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: textColor },
          },
          title: {
            display: true,
            text: "Urgency Distribution",
            color: textColor,
          },
        },
      },
    });

    // Cleanup
    return () => {
      timelineChart.current?.destroy();
      urgencyChart.current?.destroy();
    };
  }, [dashboardData]);

  // Start polling for real-time updates
  useEffect(() => {
    if (!isPolling || !app) return;

    const pollInterval = setInterval(async () => {
      try {
        console.log("[Polling] Fetching latest stats...");
        const result = await app.callServerTool({
          name: "poll-incident-stats",
          arguments: {},
        });

        if (result.structuredContent) {
          const stats = result.structuredContent as unknown as IncidentStats;
          setCurrentStats(stats);
          setLastUpdate(new Date(stats.timestamp).toLocaleTimeString());
          console.log("[Polling] Stats updated:", stats);
        }
      } catch (error) {
        console.error("[Polling] Error:", error);
      }
    }, 30000); // Poll every 30 seconds

    // Initial poll
    app
      .callServerTool({ name: "poll-incident-stats", arguments: {} })
      .then((result) => {
        if (result.structuredContent) {
          const stats = result.structuredContent as unknown as IncidentStats;
          setCurrentStats(stats);
          setLastUpdate(new Date(stats.timestamp).toLocaleTimeString());
        }
      })
      .catch(console.error);

    return () => clearInterval(pollInterval);
  }, [app, isPolling]);

  const togglePolling = useCallback(() => {
    setIsPolling((prev) => !prev);
  }, []);

  return (
    <main
      style={{
        padding: "20px",
        paddingTop: hostContext?.safeAreaInsets?.top,
        paddingRight: hostContext?.safeAreaInsets?.right,
        paddingBottom: hostContext?.safeAreaInsets?.bottom,
        paddingLeft: hostContext?.safeAreaInsets?.left,
      }}
    >
      {/* Header */}
      <header style={{ marginBottom: "24px" }}>
        <h1 style={{ margin: "0 0 8px 0", fontSize: "24px" }}>
          PagerDuty Incident Dashboard
        </h1>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <button
            onClick={togglePolling}
            style={{
              padding: "6px 12px",
              borderRadius: "4px",
              border: "1px solid var(--color-border)",
              background: isPolling ? "#10b981" : "#6b7280",
              color: "white",
              cursor: "pointer",
            }}
          >
            {isPolling ? "⏸ Pause Updates" : "▶ Resume Updates"}
          </button>
          <span style={{ fontSize: "14px", color: "var(--color-text-secondary)" }}>
            {isPolling && lastUpdate ? `Last update: ${lastUpdate}` : "Updates paused"}
          </span>
        </div>
      </header>

      {/* Summary Cards */}
      <section style={{ marginBottom: "24px" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "16px",
          }}
        >
          <MetricCard
            label="Total Incidents"
            value={dashboardData.summary.total_incidents}
            variant="default"
          />
          <MetricCard
            label="Active Incidents"
            value={currentStats?.active_incidents ?? dashboardData.summary.active_incidents}
            variant={
              (currentStats?.active_incidents ?? 0) > 0 ? "warning" : "success"
            }
          />
          <MetricCard
            label="Resolved Today"
            value={dashboardData.summary.resolved_today}
            variant="success"
          />
          <MetricCard
            label="Avg Resolution Time"
            value={
              dashboardData.summary.avg_resolution_time_minutes
                ? `${Math.round(dashboardData.summary.avg_resolution_time_minutes)}m`
                : "N/A"
            }
            variant="default"
          />
        </div>
      </section>

      {/* Charts Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        {/* Timeline Chart */}
        <section
          style={{
            background: "var(--color-card-bg)",
            padding: "16px",
            borderRadius: "8px",
            border: "1px solid var(--color-border)",
          }}
        >
          <div style={{ height: "300px" }}>
            <canvas ref={timelineChartRef}></canvas>
          </div>
        </section>

        {/* Urgency Donut Chart */}
        <section
          style={{
            background: "var(--color-card-bg)",
            padding: "16px",
            borderRadius: "8px",
            border: "1px solid var(--color-border)",
          }}
        >
          <div style={{ height: "300px" }}>
            <canvas ref={urgencyChartRef}></canvas>
          </div>
        </section>
      </div>

      {/* Service Health Grid */}
      <section
        style={{
          background: "var(--color-card-bg)",
          padding: "16px",
          borderRadius: "8px",
          border: "1px solid var(--color-border)",
        }}
      >
        <h2 style={{ margin: "0 0 16px 0", fontSize: "18px" }}>
          Service Health
        </h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr
                style={{
                  borderBottom: "2px solid var(--color-border)",
                  textAlign: "left",
                }}
              >
                <th style={{ padding: "8px" }}>Service</th>
                <th style={{ padding: "8px" }}>Incidents</th>
                <th style={{ padding: "8px" }}>High Urgency</th>
                <th style={{ padding: "8px" }}>Avg Resolution</th>
                <th style={{ padding: "8px" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.service_health.slice(0, 10).map((service) => (
                <tr
                  key={service.service_id}
                  style={{ borderBottom: "1px solid var(--color-border)" }}
                >
                  <td style={{ padding: "8px" }}>{service.service_name}</td>
                  <td style={{ padding: "8px" }}>{service.incident_count}</td>
                  <td style={{ padding: "8px" }}>{service.high_urgency_count}</td>
                  <td style={{ padding: "8px" }}>
                    {service.avg_resolution_time_minutes
                      ? `${Math.round(service.avg_resolution_time_minutes)}m`
                      : "—"}
                  </td>
                  <td style={{ padding: "8px" }}>
                    <StatusBadge status={service.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Recent Incidents (from polling) */}
      {currentStats && currentStats.recent_incidents.length > 0 && (
        <section
          style={{
            background: "var(--color-card-bg)",
            padding: "16px",
            borderRadius: "8px",
            border: "1px solid var(--color-border)",
            marginTop: "16px",
          }}
        >
          <h2 style={{ margin: "0 0 16px 0", fontSize: "18px" }}>
            Recent Active Incidents
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {currentStats.recent_incidents.map((incident) => (
              <div
                key={incident.id}
                style={{
                  padding: "12px",
                  background: "var(--color-bg)",
                  borderRadius: "4px",
                  border: "1px solid var(--color-border)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                  <div style={{ flex: 1 }}>
                    <span
                      style={{
                        fontSize: "12px",
                        color: "var(--color-text-secondary)",
                      }}
                    >
                      #{incident.incident_number}
                    </span>
                    <h3 style={{ margin: "4px 0", fontSize: "14px" }}>
                      {incident.title}
                    </h3>
                    <p style={{ margin: "4px 0", fontSize: "12px", color: "var(--color-text-secondary)" }}>
                      {incident.service_name} • Created {formatRelativeTime(incident.created_at)}
                    </p>
                  </div>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <StatusBadge status={incident.status as any} />
                    <UrgencyBadge urgency={incident.urgency} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

// Helper Components
interface MetricCardProps {
  label: string;
  value: string | number;
  variant?: "default" | "success" | "warning" | "danger";
}

function MetricCard({ label, value, variant = "default" }: MetricCardProps) {
  const colors = {
    default: "#6b7280",
    success: "#10b981",
    warning: "#f59e0b",
    danger: "#ef4444",
  };

  return (
    <div
      style={{
        background: "var(--color-card-bg)",
        padding: "16px",
        borderRadius: "8px",
        border: "1px solid var(--color-border)",
      }}
    >
      <div
        style={{
          fontSize: "28px",
          fontWeight: "bold",
          color: colors[variant],
          marginBottom: "4px",
        }}
      >
        {value}
      </div>
      <div style={{ fontSize: "14px", color: "var(--color-text-secondary)" }}>
        {label}
      </div>
    </div>
  );
}

interface StatusBadgeProps {
  status: "healthy" | "warning" | "critical" | "triggered" | "acknowledged" | "resolved";
}

function StatusBadge({ status }: StatusBadgeProps) {
  const styles: Record<string, { bg: string; text: string }> = {
    healthy: { bg: "#dcfce7", text: "#166534" },
    warning: { bg: "#fef3c7", text: "#92400e" },
    critical: { bg: "#fee2e2", text: "#991b1b" },
    triggered: { bg: "#fee2e2", text: "#991b1b" },
    acknowledged: { bg: "#fef3c7", text: "#92400e" },
    resolved: { bg: "#dcfce7", text: "#166534" },
  };

  const style = styles[status] || styles.warning;

  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: "12px",
        fontSize: "12px",
        fontWeight: "500",
        backgroundColor: style.bg,
        color: style.text,
      }}
    >
      {status}
    </span>
  );
}

interface UrgencyBadgeProps {
  urgency: "high" | "low";
}

function UrgencyBadge({ urgency }: UrgencyBadgeProps) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: "12px",
        fontSize: "12px",
        fontWeight: "500",
        backgroundColor: urgency === "high" ? "#fee2e2" : "#dbeafe",
        color: urgency === "high" ? "#991b1b" : "#1e40af",
      }}
    >
      {urgency}
    </span>
  );
}

// Utility function
function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

// Render app
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <IncidentDashboardApp />
  </StrictMode>
);
