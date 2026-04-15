/**
 * On-Call Schedule Visualizer - MCP Server
 *
 * Interactive calendar view of on-call schedules
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
 * Creates the On-Call Schedule Visualizer MCP server
 */
export function createServer(): McpServer {
  const server = new McpServer({
    name: "On-Call Schedule Visualizer",
    version: "1.0.0",
  });

  const resourceUri = "ui://oncall-schedule-visualizer/calendar.html";

  /**
   * Main calendar tool - fetches schedules and on-call data
   */
  registerAppTool(
    server,
    "oncall-calendar",
    {
      title: "On-Call Calendar",
      description: "Interactive calendar showing on-call schedules with team filtering and timezone support",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (args: any): Promise<CallToolResult> => {
      try {
        // Mock schedule data matching PagerDuty API structure
        const now = new Date();
        const startOfWeek = new Date(now);
        startOfWeek.setDate(now.getDate() - now.getDay());
        startOfWeek.setHours(0, 0, 0, 0);

        const schedules = {
          schedules: [
            {
              id: "PSCHED1",
              name: "Primary On-Call",
              time_zone: args.time_zone || "UTC",
              shifts: [
                {
                  start: new Date(startOfWeek.getTime()).toISOString(),
                  end: new Date(startOfWeek.getTime() + 86400000 * 3.5).toISOString(),
                  user: {
                    id: "PUSER1",
                    name: "John Doe",
                    email: "john@example.com",
                  },
                },
                {
                  start: new Date(startOfWeek.getTime() + 86400000 * 3.5).toISOString(),
                  end: new Date(startOfWeek.getTime() + 86400000 * 7).toISOString(),
                  user: {
                    id: "PUSER2",
                    name: "Jane Smith",
                    email: "jane@example.com",
                  },
                },
              ],
            },
            {
              id: "PSCHED2",
              name: "Database On-Call",
              time_zone: args.time_zone || "UTC",
              shifts: [
                {
                  start: new Date(startOfWeek.getTime()).toISOString(),
                  end: new Date(startOfWeek.getTime() + 86400000 * 7).toISOString(),
                  user: {
                    id: "PUSER3",
                    name: "Bob Johnson",
                    email: "bob@example.com",
                  },
                },
              ],
            },
          ],
          teams: [
            { id: "PTEAM1", name: "Infrastructure" },
            { id: "PTEAM2", name: "Database" },
          ],
          view_settings: {
            view: args.view || "week",
            time_zone: args.time_zone || "UTC",
            since: args.since || startOfWeek.toISOString(),
            until: args.until || new Date(startOfWeek.getTime() + 86400000 * 7).toISOString(),
          },
        };

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(schedules),
            },
          ],
        };
      } catch (error) {
        console.error("Error fetching schedules:", error);
        throw error;
      }
    },
  );

  /**
   * Create schedule override
   */
  registerAppTool(
    server,
    "create-schedule-override",
    {
      title: "Create Schedule Override",
      description: "Create an override for on-call schedule",
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
              override: {
                schedule_id: args.schedule_id,
                user_id: args.user_id,
                start: args.start,
                end: args.end,
              },
              message: "Override created successfully",
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
