/**
 * Service Dependency Graph - MCP Server
 *
 * Visualizes relationships between technical services and business services,
 * with incident impact overlaid on the graph.
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
    name: "Service Dependency Graph",
    version: "1.0.0",
  });

  const resourceUri = "ui://service-dependency-graph/graph.html";

  registerAppTool(
    server,
    "service-dependency-graph",
    {
      title: "Service Dependency Graph",
      description:
        "Interactive hierarchical graph showing relationships between technical services and business services, with incident impact visualization",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      // Return seed data; the React app fetches live data via callServerTool
      const graphData = {
        type: "Service Dependency Graph",
        description: "Interactive visualization of PagerDuty service dependencies and incident impact",
        instructions: "The app will load business services, technical services, and their dependencies. Active incidents are overlaid on the graph to show impact.",
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(graphData),
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
