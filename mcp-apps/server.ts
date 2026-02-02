import {
  RESOURCE_MIME_TYPE,
  registerAppResource,
  registerAppTool,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type {
  CallToolResult,
  ReadResourceResult,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "node:fs/promises";
import path from "node:path";
import {
  getRecentIncidents,
  getActiveIncidents,
  listServices,
} from "./lib/pagerduty-client.js";
import {
  generateDashboardData,
  generateIncidentStats,
} from "./lib/aggregations.js";
import {
  IncidentDashboardDataSchema,
  IncidentStatsSchema,
  DashboardInputSchema,
} from "./lib/schemas.js";

// Works both from source (server.ts) and compiled (dist/server.js)
const DIST_DIR = import.meta.filename.endsWith(".ts")
  ? path.join(import.meta.dirname, "dist")
  : import.meta.dirname;

// =============================================================================
// MCP Server
// =============================================================================

export function createServer(): McpServer {
  const server = new McpServer({
    name: "PagerDuty Visualization Server",
    version: "0.1.0",
  });

  const resourceUri = "ui://incident-dashboard/mcp-app.html";
  const simpleResourceUri = "ui://incident-dashboard/simple-dashboard.html";

  // Model-facing tool: returns initial dashboard data and opens UI (simple version)
  registerAppTool(
    server,
    "get-incident-dashboard",
    {
      title: "Get Incident Dashboard",
      description:
        "Displays an interactive dashboard with incident trends, service health, and MTTR analytics. Shows incidents over 24h, 7d, or 30d.",
      inputSchema: DashboardInputSchema.shape,
      outputSchema: IncidentDashboardDataSchema.shape,
      _meta: { ui: { resourceUri: simpleResourceUri } },
    },
    async (params: any): Promise<CallToolResult> => {
      const timeRange =
        (params?.timeRange as "24h" | "7d" | "30d") || "24h";

      try {
        console.log(`[Dashboard] Fetching data for time range: ${timeRange}`);

        // Fetch incidents and services
        const [incidents, serviceList] = await Promise.all([
          getRecentIncidents(timeRange),
          listServices({ limit: 100 }),
        ]);

        console.log(
          `[Dashboard] Found ${incidents.length} incidents and ${serviceList.services.length} services`
        );

        // Generate dashboard data
        const dashboardData = generateDashboardData(
          incidents,
          serviceList.services,
          timeRange
        );

        // Generate text summary for LLM
        const summary = `
📊 **PagerDuty Incident Dashboard**

**Summary (${timeRange})**:
- Total incidents: ${dashboardData.summary.total_incidents}
- Active incidents: ${dashboardData.summary.active_incidents}
- Resolved today: ${dashboardData.summary.resolved_today}
- Avg resolution time: ${
          dashboardData.summary.avg_resolution_time_minutes
            ? `${Math.round(dashboardData.summary.avg_resolution_time_minutes)} minutes`
            : "N/A"
        }

**Urgency Distribution**:
- High: ${dashboardData.urgency_distribution.high} (${dashboardData.urgency_distribution.high_percent}%)
- Low: ${dashboardData.urgency_distribution.low} (${dashboardData.urgency_distribution.low_percent}%)

**Top Services by Incident Count**:
${dashboardData.service_health
  .slice(0, 5)
  .map(
    (s, i) =>
      `${i + 1}. ${s.service_name}: ${s.incident_count} incidents (${s.status})`
  )
  .join("\n")}

*Interactive dashboard opened with charts and real-time updates*
        `.trim();

        return {
          content: [{ type: "text", text: summary }],
          structuredContent: dashboardData,
        };
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        console.error("[Dashboard] Error:", errorMessage);

        return {
          content: [
            {
              type: "text",
              text: `Failed to load incident dashboard: ${errorMessage}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // App-only tool: returns real-time stats for polling
  registerAppTool(
    server,
    "poll-incident-stats",
    {
      title: "Poll Incident Stats",
      description:
        "Returns real-time incident metrics for polling. App-only tool.",
      inputSchema: {},
      outputSchema: IncidentStatsSchema.shape,
      _meta: { ui: { visibility: ["app"] } },
    },
    async (): Promise<CallToolResult> => {
      try {
        // Get currently active incidents
        const incidents = await getActiveIncidents();

        console.log(
          `[Polling] Found ${incidents.length} active incidents`
        );

        // Generate real-time stats
        const stats = generateIncidentStats(incidents);

        return {
          content: [{ type: "text", text: JSON.stringify(stats) }],
          structuredContent: stats,
        };
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        console.error("[Polling] Error:", errorMessage);

        return {
          content: [
            { type: "text", text: `Polling error: ${errorMessage}` },
          ],
          isError: true,
        };
      }
    }
  );

  // Register the app resource (HTML UI)
  registerAppResource(
    server,
    resourceUri,
    resourceUri,
    {
      mimeType: RESOURCE_MIME_TYPE,
      description: "PagerDuty Incident Dashboard UI",
    },
    async (): Promise<ReadResourceResult> => {
      const html = await fs.readFile(
        path.join(DIST_DIR, "mcp-app.html"),
        "utf-8"
      );

      return {
        contents: [
          {
            uri: resourceUri,
            mimeType: RESOURCE_MIME_TYPE,
            text: html,
          },
        ],
      };
    }
  );

  // Register the simple dashboard resource (HTML UI)
  registerAppResource(
    server,
    simpleResourceUri,
    simpleResourceUri,
    {
      mimeType: RESOURCE_MIME_TYPE,
      description: "PagerDuty Simple Incident Dashboard UI",
    },
    async (): Promise<ReadResourceResult> => {
      const html = await fs.readFile(
        path.join(DIST_DIR, "simple-dashboard.html"),
        "utf-8"
      );

      return {
        contents: [
          {
            uri: simpleResourceUri,
            mimeType: RESOURCE_MIME_TYPE,
            text: html,
          },
        ],
      };
    }
  );

  return server;
}
