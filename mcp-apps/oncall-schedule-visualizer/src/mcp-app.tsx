/**
 * On-Call Schedule Visualizer - React Client
 *
 * Interactive calendar with on-call schedules
 */

import type { McpUiHostContext } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

// Types
interface User {
  id: string;
  name: string;
  email: string;
}

interface Shift {
  start: string;
  end: string;
  user: User;
}

interface Schedule {
  id: string;
  name: string;
  time_zone: string;
  shifts: Shift[];
}

interface Team {
  id: string;
  name: string;
}

interface ScheduleData {
  schedules: Schedule[];
  teams: Team[];
  view_settings: {
    view: "week" | "month";
    time_zone: string;
    since: string;
    until: string;
  };
}

// Helper functions
function extractScheduleData(result: CallToolResult): ScheduleData | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function formatDate(iso: string, showTime: boolean = false): string {
  const date = new Date(iso);
  const options: Intl.DateTimeFormatOptions = {
    month: "short",
    day: "numeric",
  };
  if (showTime) {
    options.hour = "numeric";
    options.minute = "2-digit";
  }
  return date.toLocaleDateString("en-US", options);
}

function getWeekDays(since: string): Date[] {
  const start = new Date(since);
  const days: Date[] = [];
  for (let i = 0; i < 7; i++) {
    const day = new Date(start);
    day.setDate(start.getDate() + i);
    days.push(day);
  }
  return days;
}

// Main App Component
function OnCallCalendar() {
  const [data, setData] = useState<ScheduleData | null>(null);
  const [selectedTeams, setSelectedTeams] = useState<string[]>([]);
  const [hostContext, setHostContext] = useState<McpUiHostContext | undefined>();
  const [error, setError] = useState<string | null>(null);

  const { app, error: connectionError } = useApp({
    appInfo: { name: "On-Call Calendar", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      app.ontoolresult = async (result) => {
        const newData = extractScheduleData(result);
        if (newData) {
          setData(newData);
          setError(null);
        }
      };

      app.onerror = (err) => {
        console.error("App error:", err);
        setError(err.message);
      };

      app.onhostcontextchanged = (params) => {
        setHostContext((prev) => ({ ...prev, ...params }));
      };
    },
  });

  useEffect(() => {
    if (app) {
      setHostContext(app.getHostContext());
    }
  }, [app]);

  const handleViewChange = useCallback(
    async (view: "week" | "month") => {
      if (!app || !data) return;

      try {
        const result = await app.callServerTool({
          name: "oncall-calendar",
          arguments: {
            ...data.view_settings,
            view,
            team_ids: selectedTeams,
          },
        });

        const newData = extractScheduleData(result);
        if (newData) {
          setData(newData);
        }
      } catch (err) {
        console.error("Failed to change view:", err);
      }
    },
    [app, data, selectedTeams],
  );

  const handleCreateOverride = useCallback(
    async (scheduleId: string, shift: Shift) => {
      if (!app) return;

      const userName = prompt("Enter user name for override:");
      if (!userName) return;

      try {
        await app.callServerTool({
          name: "create-schedule-override",
          arguments: {
            schedule_id: scheduleId,
            user_id: "PUSER_OVERRIDE",
            start: shift.start,
            end: shift.end,
          },
        });

        alert("Override created successfully");

        // Refresh calendar
        const result = await app.callServerTool({
          name: "oncall-calendar",
          arguments: data?.view_settings || {},
        });

        const newData = extractScheduleData(result);
        if (newData) {
          setData(newData);
        }
      } catch (err) {
        console.error("Failed to create override:", err);
        alert("Failed to create override");
      }
    },
    [app, data],
  );

  if (connectionError) {
    return (
      <div className="error-container">
        <h2>Connection Error</h2>
        <p>{connectionError.message}</p>
      </div>
    );
  }

  if (!app) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Connecting to On-Call Calendar...</p>
      </div>
    );
  }

  return (
    <CalendarView
      data={data}
      selectedTeams={selectedTeams}
      setSelectedTeams={setSelectedTeams}
      onViewChange={handleViewChange}
      onCreateOverride={handleCreateOverride}
      hostContext={hostContext}
      error={error}
    />
  );
}

// Calendar View Component
interface CalendarViewProps {
  data: ScheduleData | null;
  selectedTeams: string[];
  setSelectedTeams: (teams: string[]) => void;
  onViewChange: (view: "week" | "month") => void;
  onCreateOverride: (scheduleId: string, shift: Shift) => void;
  hostContext?: McpUiHostContext;
  error: string | null;
}

function CalendarView({
  data,
  selectedTeams,
  setSelectedTeams,
  onViewChange,
  onCreateOverride,
  hostContext,
  error,
}: CalendarViewProps) {
  if (!data) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading calendar...</p>
      </div>
    );
  }

  const weekDays = getWeekDays(data.view_settings.since);

  return (
    <main
      className="calendar-container"
      style={{
        paddingTop: hostContext?.safeAreaInsets?.top,
        paddingRight: hostContext?.safeAreaInsets?.right,
        paddingBottom: hostContext?.safeAreaInsets?.bottom,
        paddingLeft: hostContext?.safeAreaInsets?.left,
      }}
    >
      {/* Header */}
      <header className="calendar-header">
        <h1>📅 On-Call Schedule</h1>
        <div className="header-controls">
          <div className="view-toggle">
            <button
              className={data.view_settings.view === "week" ? "active" : ""}
              onClick={() => onViewChange("week")}
            >
              Week
            </button>
            <button
              className={data.view_settings.view === "month" ? "active" : ""}
              onClick={() => onViewChange("month")}
            >
              Month
            </button>
          </div>
          <select className="timezone-select" defaultValue={data.view_settings.time_zone}>
            <option value="UTC">UTC</option>
            <option value="America/New_York">Eastern</option>
            <option value="America/Chicago">Central</option>
            <option value="America/Denver">Mountain</option>
            <option value="America/Los_Angeles">Pacific</option>
          </select>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Team Filters */}
      <div className="team-filters">
        <strong>Teams:</strong>
        {data.teams.map((team) => (
          <label key={team.id} className="team-checkbox">
            <input
              type="checkbox"
              checked={selectedTeams.includes(team.id)}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedTeams([...selectedTeams, team.id]);
                } else {
                  setSelectedTeams(selectedTeams.filter((id) => id !== team.id));
                }
              }}
            />
            {team.name}
          </label>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="calendar-grid">
        {/* Day Headers */}
        <div className="calendar-header-row">
          {weekDays.map((day, i) => (
            <div key={i} className="day-header">
              <div className="day-name">{day.toLocaleDateString("en-US", { weekday: "short" })}</div>
              <div className="day-date">{day.getDate()}</div>
            </div>
          ))}
        </div>

        {/* Schedule Rows */}
        {data.schedules.map((schedule) => (
          <div key={schedule.id} className="schedule-row">
            <div className="schedule-label">{schedule.name}</div>
            <div className="schedule-shifts">
              {schedule.shifts.map((shift, shiftIdx) => (
                <ShiftBlock
                  key={shiftIdx}
                  shift={shift}
                  weekStart={weekDays[0]}
                  onCreateOverride={() => onCreateOverride(schedule.id, shift)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="calendar-legend">
        <span className="legend-item">
          <div className="legend-color" style={{ background: "#4299e1" }}></div>
          Currently on-call
        </span>
        <span className="legend-item">
          <div className="legend-color" style={{ background: "#9f7aea" }}></div>
          Override
        </span>
        <span className="legend-tip">💡 Click on shifts to create overrides</span>
      </div>
    </main>
  );
}

// Shift Block Component
interface ShiftBlockProps {
  shift: Shift;
  weekStart: Date;
  onCreateOverride: () => void;
}

function ShiftBlock({ shift, weekStart, onCreateOverride }: ShiftBlockProps) {
  const shiftStart = new Date(shift.start);
  const shiftEnd = new Date(shift.end);

  // Calculate position and width
  const weekStartTime = weekStart.getTime();
  const weekDurationMs = 7 * 24 * 60 * 60 * 1000;

  const startOffset = ((shiftStart.getTime() - weekStartTime) / weekDurationMs) * 100;
  const duration = ((shiftEnd.getTime() - shiftStart.getTime()) / weekDurationMs) * 100;

  // Clamp to visible range
  const left = Math.max(0, Math.min(100, startOffset));
  const width = Math.max(0, Math.min(100 - left, duration));

  if (width <= 0) return null;

  return (
    <div
      className="shift-block"
      style={{
        left: `${left}%`,
        width: `${width}%`,
      }}
      onClick={onCreateOverride}
      title={`${shift.user.name}\n${formatDate(shift.start, true)} - ${formatDate(shift.end, true)}`}
    >
      <span className="shift-user">{shift.user.name}</span>
    </div>
  );
}

// Render
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <OnCallCalendar />
  </StrictMode>,
);
