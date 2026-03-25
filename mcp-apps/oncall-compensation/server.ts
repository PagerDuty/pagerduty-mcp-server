/**
 * Oncall Compensation Report - MCP Server
 *
 * Shows per-user oncall hours, incident count, incident response hours,
 * and interruption rate over a configurable date range.
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

export function createServer(): McpServer {
  const server = new McpServer({
    name: "Oncall Compensation Report",
    version: "1.0.0",
  });

  const resourceUri = "ui://oncall-compensation/report.html";

  registerAppTool(
    server,
    "oncall-compensation",
    {
      title: "Oncall Compensation Report",
      description:
        "Per-user oncall compensation metrics: scheduled hours, incident count, incident response hours, and interruption rate over a configurable date range",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              type: "Oncall Compensation Report",
              description:
                "Interactive report showing oncall hours and incident response metrics per user",
              instructions:
                "The app fetches oncall shifts and incident data to calculate per-user compensation metrics.",
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
        contents: [
          { uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html },
        ],
      };
    },
  );

  return server;
}
