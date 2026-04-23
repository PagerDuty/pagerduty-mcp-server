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

export function createServer(): McpServer {
  const server = new McpServer({
    name: "On-Call Manager",
    version: "1.0.0",
  });

  const resourceUri = "ui://oncall-manager/dashboard.html";

  registerAppTool(
    server,
    "oncall-manager",
    {
      title: "On-Call Manager",
      description:
        "Personal on-call schedule view with 7-day countdown and team override management",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              status: "ready",
              message:
                "On-Call Manager UI initialized. Calls get_user_data, list_oncalls, list_schedules, list_schedule_users, and create_schedule_override.",
            }),
          },
        ],
      };
    },
  );

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
        contents: [{ uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html }],
      };
    },
  );

  return server;
}
