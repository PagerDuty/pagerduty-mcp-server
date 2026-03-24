/**
 * ImpactSidebar - Collapsible panel showing active incidents with search
 */

import { useState } from "react";
import type { ActiveIncident } from "../api";

interface Props {
  incidents: ActiveIncident[];
  collapsed: boolean;
  onToggle: () => void;
  onIncidentClick?: (incidentId: string) => void;
}

export function ImpactSidebar({ incidents, collapsed, onToggle, onIncidentClick }: Props) {
  const [search, setSearch] = useState("");

  const totalCount = incidents.length;
  const hasTrigger = incidents.some((i) => i.status === "triggered");
  const badgeClass = hasTrigger ? "" : "warn";

  const filtered = search.trim()
    ? incidents.filter(
        (i) =>
          i.title.toLowerCase().includes(search.toLowerCase()) ||
          i.service?.summary.toLowerCase().includes(search.toLowerCase())
      )
    : incidents;

  const triggered = filtered.filter((i) => i.status === "triggered");
  const acknowledged = filtered.filter((i) => i.status === "acknowledged");

  return (
    <aside className={`sidebar${collapsed ? " collapsed" : ""}`}>
      <div className="sidebar-header">
        {collapsed ? (
          // Collapsed: just the toggle + badge stacked
          <div className="sidebar-collapsed-content">
            <button className="sidebar-toggle" onClick={onToggle} title="Expand panel">
              <ChevronLeft />
            </button>
            {totalCount > 0 && (
              <span className={`incident-count-badge ${badgeClass}`}>{totalCount}</span>
            )}
          </div>
        ) : (
          <>
            <div className="sidebar-header-left">
              <span>Active Incidents</span>
              {totalCount > 0 && (
                <span className={`incident-count-badge ${badgeClass}`}>{totalCount}</span>
              )}
            </div>
            <button className="sidebar-toggle" onClick={onToggle} title="Collapse panel">
              <ChevronRight />
            </button>
          </>
        )}
      </div>

      {!collapsed && (
        <>
          <div className="sidebar-search">
            <div className="sidebar-search-wrap">
              <SearchIcon className="sidebar-search-icon" />
              <input
                type="text"
                placeholder="Search incidents…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          <div className="sidebar-content">
            {incidents.length === 0 ? (
              <div className="empty-state" style={{ height: "auto", paddingTop: 28 }}>
                <div className="empty-state-icon">✅</div>
                <div className="empty-state-title">All Clear</div>
                <div className="empty-state-text">No active incidents affecting services.</div>
              </div>
            ) : filtered.length === 0 ? (
              <div className="no-results">No matches for "{search}"</div>
            ) : (
              <>
                {triggered.length > 0 && (
                  <>
                    <div className="section-title">Triggered</div>
                    {triggered.map((inc) => (
                      <IncidentItem key={inc.id} incident={inc} onClick={onIncidentClick} />
                    ))}
                  </>
                )}
                {acknowledged.length > 0 && (
                  <>
                    <div className="section-title">Acknowledged</div>
                    {acknowledged.map((inc) => (
                      <IncidentItem key={inc.id} incident={inc} onClick={onIncidentClick} />
                    ))}
                  </>
                )}
              </>
            )}
          </div>
        </>
      )}
    </aside>
  );
}

function IncidentItem({ incident, onClick }: { incident: ActiveIncident; onClick?: (id: string) => void }) {
  return (
    <div
      className="incident-item"
      onClick={() => onClick?.(incident.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick?.(incident.id)}
    >
      <div className="incident-item-header">
        <span className="incident-title">
          <span className={`status-dot ${incident.status}`} />
          {incident.title}
        </span>
        <span className={`urgency-badge ${incident.urgency}`}>{incident.urgency}</span>
      </div>
      {incident.service && (
        <div className="incident-service">{incident.service.summary}</div>
      )}
    </div>
  );
}

function ChevronLeft() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}
