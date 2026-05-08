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
    name: "Onboarding Wizard",
    version: "1.0.0",
  });

  const resourceUri = "ui://onboarding-wizard/mcp-app.html";

  registerAppTool(
    server,
    "onboarding-wizard",
    {
      title: "Onboarding Wizard",
      description:
        "Guided 7-phase PagerDuty setup: Teams, Users (with CSV bulk import), Schedules, Escalation Policies, Services, AIOps, and Incident Workflows",
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
                "Onboarding Wizard UI initialized. Calls create_team, create_user, create_schedule, create_escalation_policy, create_service, and related MCP tools.",
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
