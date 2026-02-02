/**
 * Simple PagerDuty Incident Dashboard
 * Vanilla JS implementation showing incident data in a clean list format
 */

import {
  App,
  applyDocumentTheme,
  applyHostStyleVariables,
  type McpUiHostContext,
} from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// Dashboard data interface
interface DashboardData {
  summary: {
    total_incidents: number;
    active_incidents: number;
    resolved_today: number;
    avg_resolution_time_minutes: number | null;
  };
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
}

// DOM elements
const appEl = document.getElementById("app")!;
const refreshBtn = document.getElementById("refresh-btn") as HTMLButtonElement;

// State
let currentData: DashboardData | null = null;

// Helper to extract dashboard data from tool result
function extractDashboardData(result: CallToolResult): DashboardData | null {
  try {
    if (result.structuredContent) {
      return result.structuredContent as DashboardData;
    }
  } catch (e) {
    console.error("Failed to parse dashboard data:", e);
  }
  return null;
}

// Render the dashboard
function renderDashboard(data: DashboardData) {
  console.log("[Dashboard] Rendering with data:", data);

  // Filter services with incidents only
  const servicesWithIncidents = data.service_health
    .filter((s) => s.incident_count > 0)
    .sort((a, b) => {
      // Sort by status (critical first) then by incident count
      const statusOrder = { critical: 0, warning: 1, healthy: 2 };
      const statusDiff = statusOrder[a.status] - statusOrder[b.status];
      if (statusDiff !== 0) return statusDiff;
      return b.incident_count - a.incident_count;
    });

  const html = `
    <div class="summary-cards">
      <div class="card">
        <div class="card-value">${data.summary.total_incidents}</div>
        <div class="card-label">Total Incidents (${data.time_range.label})</div>
      </div>
      <div class="card">
        <div class="card-value" style="color: ${data.summary.active_incidents > 0 ? '#f59e0b' : '#10b981'}">${data.summary.active_incidents}</div>
        <div class="card-label">Active Incidents</div>
      </div>
      <div class="card">
        <div class="card-value" style="color: #10b981">${data.summary.resolved_today}</div>
        <div class="card-label">Resolved Today</div>
      </div>
      <div class="card">
        <div class="card-value">${data.summary.avg_resolution_time_minutes ? Math.round(data.summary.avg_resolution_time_minutes) + 'm' : 'N/A'}</div>
        <div class="card-label">Avg Resolution Time</div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 16px;">
      <h2 style="margin: 0 0 8px 0; font-size: 16px;">Urgency Distribution</h2>
      <div class="service-stats">
        <div>🔴 High: ${data.urgency_distribution.high} (${data.urgency_distribution.high_percent}%)</div>
        <div>🟡 Low: ${data.urgency_distribution.low} (${data.urgency_distribution.low_percent}%)</div>
      </div>
    </div>

    <div class="service-list">
      <h2 style="margin: 0 0 16px 0; font-size: 18px;">
        Services with Incidents (${servicesWithIncidents.length})
      </h2>
      ${
        servicesWithIncidents.length === 0
          ? '<p style="color: var(--color-text-secondary); text-align: center; padding: 20px;">✅ No active incidents - all services healthy!</p>'
          : servicesWithIncidents
              .map(
                (service) => `
          <div class="service-item">
            <div class="service-name">
              ${service.service_name}
              <span class="badge badge-${service.status}">${service.status.toUpperCase()}</span>
            </div>
            <div class="service-stats">
              <span>📊 ${service.incident_count} incidents</span>
              <span>🔴 ${service.high_urgency_count} high</span>
              <span>🟡 ${service.low_urgency_count} low</span>
              <span>⏱️ ${service.avg_resolution_time_minutes ? Math.round(service.avg_resolution_time_minutes) + 'm avg' : 'N/A'}</span>
            </div>
          </div>
        `
              )
              .join("")
      }
    </div>

    <div style="margin-top: 16px; font-size: 12px; color: var(--color-text-secondary); text-align: center;">
      Last updated: ${new Date().toLocaleTimeString()}
    </div>
  `;

  appEl.innerHTML = html;
}

// Show error message
function showError(message: string) {
  appEl.innerHTML = `
    <div class="error">
      <strong>❌ Error:</strong> ${message}
    </div>
  `;
}

// Show loading state
function showLoading(message = "Loading...") {
  appEl.innerHTML = `
    <div class="loading">
      <p>⏳ ${message}</p>
    </div>
  `;
}

// Handle host context changes (theme, etc.)
function handleHostContextChanged(ctx: McpUiHostContext) {
  console.log("[Dashboard] Host context changed:", ctx);
  
  if (ctx.theme) {
    applyDocumentTheme(ctx.theme);
  }
  if (ctx.styles?.variables) {
    applyHostStyleVariables(ctx.styles.variables);
  }
}

// Fetch dashboard data
async function fetchDashboardData(app: App, timeRange: string = "7d") {
  try {
    console.log(`[Dashboard] Fetching dashboard data for ${timeRange}...`);
    refreshBtn.disabled = true;
    showLoading(`Fetching ${timeRange} data...`);

    const result = await app.callServerTool({
      name: "get-incident-dashboard",
      arguments: { timeRange },
    });

    console.log("[Dashboard] Tool result:", result);

    const data = extractDashboardData(result);
    if (data) {
      currentData = data;
      renderDashboard(data);
    } else {
      showError("Failed to parse dashboard data. Check console for details.");
    }
  } catch (error: any) {
    console.error("[Dashboard] Error fetching data:", error);
    showError(error.message || "Failed to fetch dashboard data");
  } finally {
    refreshBtn.disabled = false;
  }
}

// Initialize the app
async function initApp() {
  console.log("[Dashboard] Initializing app...");

  const app = new App({
    name: "PagerDuty Simple Dashboard",
    version: "1.0.0",
  });

  // Register event handlers
  app.onteardown = async () => {
    console.info("[Dashboard] App is being torn down");
    return {};
  };

  app.ontoolinput = (params) => {
    console.info("[Dashboard] Tool call input:", params);
  };

  app.ontoolresult = (result) => {
    console.info("[Dashboard] Tool call result:", result);
  };

  app.ontoolcancelled = (params) => {
    console.info("[Dashboard] Tool call cancelled:", params.reason);
  };

  app.onerror = (error) => {
    console.error("[Dashboard] App error:", error);
    showError(error.message || "Unknown app error");
  };

  app.onhostcontextchanged = handleHostContextChanged;

  // Connect to host
  try {
    console.log("[Dashboard] Connecting to host...");
    await app.connect();
    console.log("[Dashboard] Connected successfully!");

    // Apply initial host context
    const ctx = app.getHostContext();
    if (ctx) {
      handleHostContextChanged(ctx);
    }

    // Fetch initial data
    await fetchDashboardData(app, "7d");

    // Setup refresh button
    refreshBtn.addEventListener("click", () => {
      fetchDashboardData(app, "7d");
    });

  } catch (error: any) {
    console.error("[Dashboard] Connection error:", error);
    showError(`Failed to connect to MCP host: ${error.message}`);
  }
}

// Start the app
initApp().catch((error) => {
  console.error("[Dashboard] Init error:", error);
  showError(`Failed to initialize app: ${error.message}`);
});
