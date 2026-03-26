/**
 * Service Dependency Graph - React App
 */

import type { App as McpApp } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchGraphData } from "./api";
import type { GraphData } from "./api";
import { GraphCanvas } from "./components/GraphCanvas";
import { ImpactSidebar } from "./components/ImpactSidebar";

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Service Dependency Graph", version: "1.0.0" },
    capabilities: {},
  });

  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [displayMode, setDisplayMode] = useState<"inline" | "fullscreen" | "pip">("inline");

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if (ctx.displayMode) setDisplayMode(ctx.displayMode);
    };
  }, [app]);

  useEffect(() => {
    if (!app) return;
    let cancelled = false;

    async function load(appInstance: McpApp) {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchGraphData(appInstance);
        if (!cancelled) setGraphData(data);
      } catch (err) {
        if (!cancelled) {
          console.error("[SDG] Failed to load graph data:", err);
          setError(err instanceof Error ? err.message : "Failed to load graph data");
          setGraphData({ technicalServices: [], businessServices: [], relationships: [], incidents: [], errors: [err instanceof Error ? err.message : "Failed to load graph data"] });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load(app);
    return () => { cancelled = true; };
  }, [app]);

  const displayError = connectionError?.message ?? error;

  return (
    // Always dark — matches Claude Desktop and VS Code dark environments
    <div className="app" data-theme="dark">
      <header className="header">
        <div className="header-left">
          <PagerDutyIcon />
          <div>
            <div className="header-title">Service Dependency Graph</div>
            <div className="header-subtitle">
              {graphData
                ? `${graphData.businessServices.length} business · ${graphData.technicalServices.length} technical services`
                : "Loading…"}
            </div>
          </div>
        </div>
        {/* Inline legend */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, justifyContent: "center", flexWrap: "wrap" }}>
          <LegendItem color="#3d4166" accent="#a6e3a1" label="Business Service" squared />
          <LegendItem color="#3d4166" label="Technical Service" />
          <LegendItem color="#f38ba8" bg="#3d1520" label="Active Incident" />
        </div>

        <button
          className="btn-expand"
          onClick={async () => {
            if (!app) return;
            await app.requestDisplayMode({ mode: displayMode === "fullscreen" ? "inline" : "fullscreen" });
          }}
          title={displayMode === "fullscreen" ? "Exit fullscreen" : "Expand to fullscreen"}
        >
          {displayMode === "fullscreen" ? "⤡" : "⤢"}
        </button>

        <div className="pd-badge">
          <span className="pd-dot" />
          PagerDuty
        </div>
      </header>

      <div className="main-content">
        <div className="graph-area">
          {loading && (
            <div className="loading-overlay">
              <div className="spinner" />
              <span>Loading service graph…</span>
            </div>
          )}

          {displayError && !loading && (
            <div className="error-banner">⚠ {displayError}</div>
          )}

          {graphData && !loading && (
            <GraphCanvas
              businessServices={graphData.businessServices}
              technicalServices={graphData.technicalServices}
              relationships={graphData.relationships}
              incidents={graphData.incidents}
              errors={graphData.errors}
            />
          )}

          {!loading && graphData &&
            graphData.businessServices.length === 0 &&
            graphData.technicalServices.length === 0 && (
            <div className="empty-state" style={{ position: "absolute", inset: 0 }}>
              <div className="empty-state-icon">🔗</div>
              <div className="empty-state-title">No Services Found</div>
              <div className="empty-state-text">
                No PagerDuty services are available.<br />
                Connect a PagerDuty MCP server to visualize your service graph.
              </div>
            </div>
          )}
        </div>

        <ImpactSidebar
          incidents={graphData?.incidents ?? []}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed((v) => !v)}
        />
      </div>
    </div>
  );
}

function LegendItem({ color, bg, accent, label, squared }: { color: string; bg?: string; accent?: string; label: string; squared?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#a6adc8" }}>
      <div style={{
        width: 26, height: 13,
        borderRadius: squared ? 3 : 6.5,
        border: `1.5px solid ${color}`,
        background: bg ?? "#1e1e2e",
        position: "relative", overflow: "hidden", flexShrink: 0,
      }}>
        {accent && <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 3, background: accent }} />}
      </div>
      {label}
    </div>
  );
}

function PagerDutyIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="16" fill="#06AC38" />
      <path d="M35 25h18c10 0 18 7 18 17s-8 17-18 17H47v16H35V25zm12 24h5c4.5 0 7-2.5 7-7s-2.5-7-7-7H47v14z" fill="white" />
    </svg>
  );
}

const container = document.getElementById("root");
if (container) {
  createRoot(container).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
}
