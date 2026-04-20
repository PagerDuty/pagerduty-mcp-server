/**
 * Operations Intelligence - MCP Server
 *
 * Team operational health dashboard with Analytics API metrics and AI insights
 */
import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE, } from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import fs from "node:fs/promises";
import path from "node:path";
const DIST_DIR = import.meta.dirname;
/**
 * Creates the Operations Intelligence MCP server
 */
export function createServer() {
    const server = new McpServer({
        name: "Operations Intelligence",
        version: "2.0.0",
    });
    const resourceUri = "ui://operations-intelligence/dashboard.html";
    /**
     * Main dashboard tool — opens the Operations Intelligence UI
     */
    registerAppTool(server, "operations-intelligence", {
        title: "Operations Intelligence",
        description: "Team operational health dashboard — KPI bar, service/team/responder analytics tables, and AI-powered insights tab",
        inputSchema: {},
        _meta: { ui: { resourceUri } },
    }, async (_args) => {
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify({
                        status: "ready",
                        message: "Operations Intelligence UI initialized. The UI calls get_incident_metrics_by_service, get_incident_metrics_by_team, get_responder_load_metrics, list_teams, and insights_agent_tool to power the Operational and Insights tabs.",
                    }),
                },
            ],
        };
    });
    /**
     * Register the UI resource
     */
    registerAppResource(server, resourceUri, resourceUri, { mimeType: RESOURCE_MIME_TYPE }, async () => {
        const html = await fs.readFile(path.join(DIST_DIR, "mcp-app.html"), "utf-8");
        return {
            contents: [
                { uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html },
            ],
        };
    });
    return server;
}
