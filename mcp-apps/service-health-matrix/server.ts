/**
 * Service Health Matrix - MCP Server
 *
 * Health Check analysis organized by PagerDuty object type
 * Uses parent pagerduty-mcp server tools for data fetching
 */

import {
  registerAppResource,
  registerAppTool,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const DIST_DIR = path.dirname(__filename);

/**
 * Creates the Service Health Matrix MCP server
 */
export function createServer(): McpServer {
  const server = new McpServer({
    name: "PagerDuty Health Check Matrix",
    version: "1.0.0",
  });

  const resourceUri = "ui://service-health-matrix/grid.html";

  /**
   * Main matrix tool - triggers health check UI
   * The UI will call parent server tools (list_services, list_users, etc.) to fetch data
   */
  registerAppTool(
    server,
    "service-health-matrix",
    {
      title: "PagerDuty Health Check Matrix",
      description: "Comprehensive health check analysis organized by object type (Services, Teams, Users, Escalation Policies, Schedules). The UI will call list_services, list_users, list_teams, list_escalation_policies, list_schedules, and list_incidents tools to fetch real data.",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      // This tool just triggers the UI
      // The UI will call parent server tools to fetch data
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              status: "ready",
              message: "Health Check Matrix UI initialized. Fetching data from PagerDuty...",
            }),
          },
        ],
      };
    },
  );

  /**
   * Get detailed health check information
   */
  registerAppTool(
    server,
    "get-health-check-details",
    {
      title: "Get Health Check Details",
      description: "Fetch detailed information about a specific health check",
      inputSchema: {
        type: "object",
        properties: {
          health_check_id: {
            type: "string",
            description: "The ID of the health check",
          },
          object_id: {
            type: "string",
            description: "The ID of the PagerDuty object",
          },
        },
        required: ["health_check_id", "object_id"],
      } as any,
      _meta: { ui: { resourceUri } },
    },
    async (args: any): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              health_check_id: args.health_check_id,
              object_id: args.object_id,
              details: "Detailed health check analysis",
              recommendations: [
                "Review the health check criteria",
                "Understand the impact",
                "Take corrective action to resolve the issue",
              ],
            }),
          },
        ],
      };
    },
  );

  /**
   * Register the UI resource
   */
  registerAppResource(
    server,
    resourceUri,
    resourceUri,
    { mimeType: RESOURCE_MIME_TYPE },
    async () => {
      const html = await fs.readFile(
        path.join(DIST_DIR, "mcp-app.html"),
        "utf-8",
      );

      return {
        contents: [
          { uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html },
        ],
      };
    },
  );

  return server;
}
