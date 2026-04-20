/**
 * Post-Mortem Builder - MCP Server
 *
 * Timeline-based post-mortem builder from incident data
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
 * Creates the Post-Mortem Builder MCP server
 */
export function createServer(): McpServer {
  const server = new McpServer({
    name: "Post-Mortem Builder",
    version: "1.0.0",
  });

  const resourceUri = "ui://post-mortem-builder/builder.html";

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

  registerAppTool(
    server,
    "post-mortem-builder",
    {
      title: "Post-Mortem Builder",
      description:
        "Build a structured post-mortem from a resolved incident's timeline, log entries, notes, and change events",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ status: "ready", message: "Post-Mortem Builder is open" }),
          },
        ],
      };
    },
  );

  return server;
}
