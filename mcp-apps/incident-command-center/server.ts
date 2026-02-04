/**
 * Incident Command Center - MCP Server
 *
 * Real-time PagerDuty incident management dashboard
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

const DIST_DIR = import.meta.dirname;

/**
 * Creates the Incident Command Center MCP server
 */
export function createServer(): McpServer {
  const server = new McpServer({
    name: "Incident Command Center",
    version: "1.0.0",
  });

  const resourceUri = "ui://incident-command-center/dashboard.html";

  /**
   * Main dashboard tool - fetches incidents with full context
   */
  registerAppTool(
    server,
    "incident-command-center",
    {
      title: "Incident Command Center",
      description: "Real-time incident management dashboard with AI-powered insights and quick actions",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (args: any): Promise<CallToolResult> => {
      try {
        // This would integrate with your PagerDuty MCP tools
        // For now, returning mock structure that matches PagerDuty API
        const incidents = {
          incidents: [
            {
              id: "Q1234567",
              incident_number: 1234,
              title: "High CPU usage on production-api-01",
              status: "triggered",
              urgency: "high",
              created_at: new Date(Date.now() - 1800000).toISOString(),
              service: {
                id: "PSERVICE1",
                summary: "Production API",
              },
              assignments: [
                {
                  assignee: {
                    id: "PUSER1",
                    summary: "John Doe",
                  },
                },
              ],
              alert_counts: {
                triggered: 5,
                resolved: 0,
              },
            },
            {
              id: "Q1234568",
              incident_number: 1235,
              title: "Database connection timeout",
              status: "acknowledged",
              urgency: "high",
              created_at: new Date(Date.now() - 3600000).toISOString(),
              service: {
                id: "PSERVICE2",
                summary: "Database Service",
              },
              assignments: [
                {
                  assignee: {
                    id: "PUSER2",
                    summary: "Jane Smith",
                  },
                },
              ],
              alert_counts: {
                triggered: 3,
                resolved: 2,
              },
            },
          ],
          filters: {
            status: args.status || ["triggered", "acknowledged"],
            urgency: args.urgency || [],
            auto_refresh: args.auto_refresh !== false,
          },
          metadata: {
            timestamp: new Date().toISOString(),
            total_count: 2,
          },
        };

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(incidents),
            },
          ],
        };
      } catch (error) {
        console.error("Error fetching incidents:", error);
        throw error;
      }
    },
  );

  /**
   * Get similar/past incidents using AI
   */
  registerAppTool(
    server,
    "get-similar-incidents",
    {
      title: "Get Similar Incidents",
      description: "Fetch past and related incidents for context",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      // Mock similar incidents data
      const similar = {
        past_incidents: [
          {
            id: "Q1234560",
            incident_number: 1230,
            title: "High CPU usage on production-api-02",
            created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
            resolved_at: new Date(Date.now() - 86400000 * 7 + 3600000).toISOString(),
            similarity_score: 0.92,
          },
        ],
        related_incidents: [
          {
            id: "Q1234569",
            incident_number: 1236,
            title: "Increased latency on API endpoints",
            status: "acknowledged",
            created_at: new Date(Date.now() - 1200000).toISOString(),
            service: {
              summary: "API Gateway",
            },
          },
        ],
      };

      return {
        content: [{ type: "text", text: JSON.stringify(similar) }],
      };
    },
  );

  /**
   * Quick action tool - acknowledge, resolve, or escalate
   */
  registerAppTool(
    server,
    "incident-quick-action",
    {
      title: "Incident Quick Action",
      description: "Perform quick actions on incidents",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (args: any): Promise<CallToolResult> => {
      // This would call manage_incidents tool
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              action: args.action,
              incident_ids: args.incident_ids,
              message: `Successfully ${args.action}d ${args.incident_ids.length} incident(s)`,
            }),
          },
        ],
      };
    },
  );

  /**
   * Add note to incident
   */
  registerAppTool(
    server,
    "add-incident-note",
    {
      title: "Add Incident Note",
      description: "Add a note to an incident",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (args: any): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              incident_id: args.incident_id,
              message: "Note added successfully",
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
