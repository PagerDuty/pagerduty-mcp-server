/**
 * Service Health Matrix - React Client
 *
 * Health Check visualization using parent PagerDuty MCP server tools
 */

import type { McpUiHostContext } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { HEALTH_CHECKS } from "../health-checks.js";
import "./styles.css";

// Types
interface HealthCheck {
  id: string;
  status: "pass" | "warning" | "fail";
  severity: string;
  current_value: string;
  expected_value: string;
}

interface PdObject {
  id: string;
  name: string;
  health_checks: HealthCheck[];
  teams?: string[];
  team?: string;
  member_count?: number;
  service_count?: number;
  user_count?: number;
  role?: string;
}

interface MatrixData {
  services: PdObject[];
  teams: PdObject[];
  escalation_policies: PdObject[];
  users: PdObject[];
  schedules: PdObject[];
  metadata: {
    timestamp: string;
    total_health_checks: number;
    passing: number;
    warning: number;
    failing: number;
  };
}

type ObjectType = "services" | "teams" | "escalation_policies" | "users" | "schedules";

// Helper functions
function getStatusColor(status: string): string {
  switch (status) {
    case "pass": return "#48bb78";
    case "warning": return "#ed8936";
    case "fail": return "#e53e3e";
    default: return "#a0aec0";
  }
}

function getStatusEmoji(status: string): string {
  switch (status) {
    case "pass": return "✅";
    case "warning": return "⚠️";
    case "fail": return "❌";
    default: return "🔍";
  }
}

function getSeverityColor(severity: string): string {
  switch (severity) {
    case "critical": return "#e53e3e";
    case "major": return "#ed8936";
    case "high": return "#f6ad55";
    case "medium": return "#4299e1";
    case "low": return "#48bb78";
    default: return "#a0aec0";
  }
}

function getObjectTypeLabel(type: ObjectType): string {
  const labels = {
    services: "🔧 Services",
    teams: "👥 Teams",
    escalation_policies: "🚨 Escalation Policies",
    users: "👤 Users",
    schedules: "📅 Schedules",
  };
  return labels[type];
}

// Health check evaluation functions
function evaluateServiceHealthChecks(service: any, incidents: any[]): HealthCheck[] {
  const serviceIncidents = incidents.filter(inc => inc.service?.id === service.id);
  const triggeredIncidents = serviceIncidents.filter(inc => inc.status === 'triggered');
  const acknowledgedIncidents = serviceIncidents.filter(inc => inc.status === 'acknowledged');
  const activeIncidents = serviceIncidents.filter(inc => inc.status === 'triggered' || inc.status === 'acknowledged');

  const checks: HealthCheck[] = [];

  // service-triggered-count
  const triggeredCheck = HEALTH_CHECKS.find(hc => hc.id === 'service-triggered-count');
  if (triggeredCheck) {
    checks.push({
      id: triggeredCheck.id,
      status: triggeredIncidents.length <= 1 ? 'pass' : triggeredIncidents.length <= 5 ? 'warning' : 'fail',
      severity: triggeredIncidents.length > 5 ? 'critical' : 'high',
      current_value: triggeredIncidents.length.toString(),
      expected_value: triggeredCheck.expected_value,
    });
  }

  // service-active-count
  const activeCheck = HEALTH_CHECKS.find(hc => hc.id === 'service-active-count');
  if (activeCheck) {
    checks.push({
      id: activeCheck.id,
      status: activeIncidents.length <= 1 ? 'pass' : activeIncidents.length <= 5 ? 'warning' : 'fail',
      severity: 'major',
      current_value: activeIncidents.length.toString(),
      expected_value: activeCheck.expected_value,
    });
  }

  // service-acknowledged-count
  const ackCheck = HEALTH_CHECKS.find(hc => hc.id === 'service-acknowledged-count');
  if (ackCheck) {
    checks.push({
      id: ackCheck.id,
      status: acknowledgedIncidents.length <= 1 ? 'pass' : acknowledgedIncidents.length <= 5 ? 'warning' : 'fail',
      severity: acknowledgedIncidents.length > 5 ? 'major' : 'high',
      current_value: acknowledgedIncidents.length.toString(),
      expected_value: ackCheck.expected_value,
    });
  }

  return checks;
}

function evaluateUserHealthChecks(user: any): HealthCheck[] {
  const checks: HealthCheck[] = [];

  // Note: contact_methods and notification_rules are not included in the basic user list
  // These would require individual get_user calls which would be too slow
  // For now, we skip these checks or mark them as unavailable

  // Only evaluate if we have the detailed user data
  if (user.contact_methods) {
    const contactMethods = user.contact_methods.length;
    const contactCheck = HEALTH_CHECKS.find(hc => hc.id === 'user-contact-methods');
    if (contactCheck) {
      checks.push({
        id: contactCheck.id,
        status: contactMethods >= 3 ? 'pass' : contactMethods >= 2 ? 'warning' : 'fail',
        severity: contactMethods < 2 ? 'critical' : 'major',
        current_value: contactMethods.toString(),
        expected_value: contactCheck.expected_value,
      });
    }
  }

  if (user.notification_rules) {
    const notificationRules = user.notification_rules.filter((r: any) => r.urgency === 'high');
    const highUrgencyRules = notificationRules.length;

    const notifCheck = HEALTH_CHECKS.find(hc => hc.id === 'user-notification-rules');
    if (notifCheck) {
      checks.push({
        id: notifCheck.id,
        status: highUrgencyRules >= 3 ? 'pass' : highUrgencyRules >= 2 ? 'warning' : 'fail',
        severity: highUrgencyRules < 2 ? 'major' : 'high',
        current_value: highUrgencyRules.toString(),
        expected_value: notifCheck.expected_value,
      });
    }

    const delays = notificationRules.map((r: any) => r.start_delay_in_minutes || 0);
    const hasStaggered = delays.some((d: number) => d >= 1);

    const staggerCheck = HEALTH_CHECKS.find(hc => hc.id === 'user-staggered-notifications');
    if (staggerCheck) {
      checks.push({
        id: staggerCheck.id,
        status: hasStaggered ? 'pass' : 'fail',
        severity: 'major',
        current_value: hasStaggered ? 'Yes' : 'No',
        expected_value: staggerCheck.expected_value,
      });
    }
  }

  return checks;
}

function evaluateEPHealthChecks(ep: any): HealthCheck[] {
  const layers = ep.escalation_rules?.length || 0;
  const loops = ep.num_loops || 0;

  const inactiveUsers = ep.escalation_rules?.reduce((count: number, rule: any) => {
    const inactiveTargets = rule.targets?.filter((t: any) =>
      t.type === 'user_reference' && t.summary?.includes('(inactive)')
    ).length || 0;
    return count + inactiveTargets;
  }, 0) || 0;

  const hasTeam = ep.teams && ep.teams.length > 0;

  const checks: HealthCheck[] = [];

  const layersCheck = HEALTH_CHECKS.find(hc => hc.id === 'ep-layers');
  if (layersCheck) {
    checks.push({
      id: layersCheck.id,
      status: layers >= 3 ? 'pass' : layers >= 2 ? 'warning' : 'fail',
      severity: 'critical',
      current_value: layers.toString(),
      expected_value: layersCheck.expected_value,
    });
  }

  const loopsCheck = HEALTH_CHECKS.find(hc => hc.id === 'ep-loops');
  if (loopsCheck) {
    checks.push({
      id: loopsCheck.id,
      status: loops > 1 ? 'pass' : loops === 1 ? 'warning' : 'fail',
      severity: 'critical',
      current_value: loops.toString(),
      expected_value: loopsCheck.expected_value,
    });
  }

  const inactiveCheck = HEALTH_CHECKS.find(hc => hc.id === 'ep-inactive-users');
  if (inactiveCheck) {
    checks.push({
      id: inactiveCheck.id,
      status: inactiveUsers === 0 ? 'pass' : inactiveUsers <= 1 ? 'warning' : 'fail',
      severity: 'critical',
      current_value: inactiveUsers.toString(),
      expected_value: inactiveCheck.expected_value,
    });
  }

  const teamCheck = HEALTH_CHECKS.find(hc => hc.id === 'ep-team-association');
  if (teamCheck) {
    checks.push({
      id: teamCheck.id,
      status: hasTeam ? 'pass' : 'warning',
      severity: 'high',
      current_value: hasTeam ? 'Yes' : 'No',
      expected_value: teamCheck.expected_value,
    });
  }

  return checks;
}

function evaluateScheduleHealthChecks(schedule: any): HealthCheck[] {
  const inactiveUsers = schedule.schedule_layers?.reduce((count: number, layer: any) => {
    const inactiveInLayer = layer.users?.filter((u: any) =>
      u.summary?.includes('(inactive)')
    ).length || 0;
    return count + inactiveInLayer;
  }, 0) || 0;

  const checks: HealthCheck[] = [];

  const inactiveCheck = HEALTH_CHECKS.find(hc => hc.id === 'schedule-inactive-users');
  if (inactiveCheck) {
    checks.push({
      id: inactiveCheck.id,
      status: inactiveUsers === 0 ? 'pass' : inactiveUsers <= 1 ? 'warning' : 'fail',
      severity: 'critical',
      current_value: inactiveUsers.toString(),
      expected_value: inactiveCheck.expected_value,
    });
  }

  return checks;
}

function evaluateTeamHealthChecks(_team: any, teamMembers: any[], teamEPs: any[]): HealthCheck[] {
  const checks: HealthCheck[] = [];
  const totalMembers = teamMembers.length;
  if (totalMembers === 0) return checks;

  // Only evaluate contact methods if we have that data
  const membersWithContactData = teamMembers.filter(m => m.contact_methods);
  if (membersWithContactData.length > 0) {
    const membersWithEnoughContactMethods = membersWithContactData.filter(m =>
      m.contact_methods.length >= 3
    ).length;
    const contactMethodsPct = (membersWithEnoughContactMethods / membersWithContactData.length) * 100;

    const contactCheck = HEALTH_CHECKS.find(hc => hc.id === 'team-contact-methods-pct');
    if (contactCheck) {
      checks.push({
        id: contactCheck.id,
        status: contactMethodsPct >= 90 ? 'pass' : contactMethodsPct >= 75 ? 'warning' : 'fail',
        severity: 'major',
        current_value: `${contactMethodsPct.toFixed(1)}%`,
        expected_value: contactCheck.expected_value,
      });
    }
  }

  // Check EP layers if we have that data
  const epsWithLayerData = teamEPs.filter(ep => ep.escalation_rules);
  if (epsWithLayerData.length > 0) {
    const epsWithEnoughLayers = epsWithLayerData.filter(ep => ep.escalation_rules.length >= 3).length;
    const epsLayersPct = (epsWithEnoughLayers / epsWithLayerData.length) * 100;

    const layersCheck = HEALTH_CHECKS.find(hc => hc.id === 'team-eps-layers');
    if (layersCheck) {
      checks.push({
        id: layersCheck.id,
        status: epsLayersPct > 75 ? 'pass' : epsLayersPct > 50 ? 'warning' : 'fail',
        severity: 'medium',
        current_value: `${epsLayersPct.toFixed(1)}%`,
        expected_value: layersCheck.expected_value,
      });
    }
  }

  return checks;
}

// Main App Component
function HealthCheckMatrix() {
  const [data, setData] = useState<MatrixData | null>(null);
  const [selectedType, setSelectedType] = useState<ObjectType>("services");
  const [selectedObject, setSelectedObject] = useState<string | null>(null);
  const [hostContext, setHostContext] = useState<McpUiHostContext | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { app, error: connectionError } = useApp({
    appInfo: { name: "PagerDuty Health Check Matrix", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      console.log("✓ App created, setting up handlers...");

      app.ontoolresult = async (result) => {
        console.log("✓ Initial tool result received:", result);
        // Initial tool result received, now fetch real data
        await fetchData();
      };

      app.onerror = (err) => {
        console.error("❌ App error:", err);
        setError(err.message);
      };

      app.onhostcontextchanged = (params) => {
        console.log("✓ Host context changed:", params);
        setHostContext((prev) => ({ ...prev, ...params }));
      };
    },
  });

  useEffect(() => {
    if (app) {
      setHostContext(app.getHostContext());
    }
  }, [app]);

  const fetchData = useCallback(async () => {
    if (!app) return;

    setLoading(true);
    setError(null);

    try {
      console.log("Fetching PagerDuty data from parent server...");
      console.log("Calling list_services...");

      // Call parent server tools in parallel with timeout
      const timeout = 30000; // 30 seconds
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error("Request timeout - tool calls took too long")), timeout)
      );

      const dataPromise = Promise.all([
        app.callServerTool({ name: "list_services", arguments: { limit: 25 } })
          .then(r => { console.log("✓ list_services complete"); return r; })
          .catch(e => { console.error("❌ list_services failed:", e); throw e; }),
        app.callServerTool({ name: "list_users", arguments: { limit: 25 } })
          .then(r => { console.log("✓ list_users complete"); return r; })
          .catch(e => { console.error("❌ list_users failed:", e); throw e; }),
        app.callServerTool({ name: "list_teams", arguments: { limit: 25 } })
          .then(r => { console.log("✓ list_teams complete"); return r; })
          .catch(e => { console.error("❌ list_teams failed:", e); throw e; }),
        app.callServerTool({ name: "list_escalation_policies", arguments: { limit: 25 } })
          .then(r => { console.log("✓ list_escalation_policies complete"); return r; })
          .catch(e => { console.error("❌ list_escalation_policies failed:", e); throw e; }),
        app.callServerTool({ name: "list_schedules", arguments: { limit: 25 } })
          .then(r => { console.log("✓ list_schedules complete"); return r; })
          .catch(e => { console.error("❌ list_schedules failed:", e); throw e; }),
        app.callServerTool({ name: "list_incidents", arguments: { statuses: ["triggered", "acknowledged"], limit: 25 } })
          .then(r => { console.log("✓ list_incidents complete"); return r; })
          .catch(e => { console.error("❌ list_incidents failed:", e); throw e; }),
      ]);

      const [servicesResult, usersResult, teamsResult, epsResult, schedulesResult, incidentsResult] = await Promise.race([
        dataPromise,
        timeoutPromise
      ]) as any[];

      // Extract data from tool results (parent server returns ListResponseModel with 'response' field)
      const servicesData = JSON.parse(servicesResult.content?.find((c: any) => c.type === "text")?.text || '{"response":[]}');
      const usersData = JSON.parse(usersResult.content?.find((c: any) => c.type === "text")?.text || '{"response":[]}');
      const teamsData = JSON.parse(teamsResult.content?.find((c: any) => c.type === "text")?.text || '{"response":[]}');
      const epsData = JSON.parse(epsResult.content?.find((c: any) => c.type === "text")?.text || '{"response":[]}');
      const schedulesData = JSON.parse(schedulesResult.content?.find((c: any) => c.type === "text")?.text || '{"response":[]}');
      const incidentsData = JSON.parse(incidentsResult.content?.find((c: any) => c.type === "text")?.text || '{"response":[]}');

      const services = servicesData.response || [];
      const users = usersData.response || [];
      const teams = teamsData.response || [];
      const escalationPolicies = epsData.response || [];
      const schedules = schedulesData.response || [];
      const incidents = incidentsData.response || [];

      console.log(`Fetched: ${services.length} services, ${users.length} users, ${teams.length} teams`);

      // Process services with health checks
      const processedServices = services.map((service: any) => ({
        id: service.id,
        name: service.name,
        teams: service.teams?.map((t: any) => t.summary) || [],
        health_checks: evaluateServiceHealthChecks(service, incidents),
      }));

      // Process users with health checks (filter to responders only)
      const processedUsers = users.filter((user: any) => user.role === 'user' || user.role === 'limited_user').map((user: any) => ({
        id: user.id,
        name: user.name,
        role: user.role,
        teams: user.teams?.map((t: any) => t.summary) || [],
        health_checks: evaluateUserHealthChecks(user),
      }));

      // Process escalation policies with health checks
      const processedEPs = escalationPolicies.map((ep: any) => ({
        id: ep.id,
        name: ep.name,
        team: ep.teams?.[0]?.summary || 'No Team',
        service_count: ep.services?.length || 0,
        health_checks: evaluateEPHealthChecks(ep),
      }));

      // Process schedules with health checks
      const processedSchedules = schedules.map((schedule: any) => ({
        id: schedule.id,
        name: schedule.name,
        team: schedule.teams?.[0]?.summary || 'No Team',
        user_count: schedule.users?.length || 0,
        health_checks: evaluateScheduleHealthChecks(schedule),
      }));

      // Process teams with aggregated health checks
      const processedTeams = teams.map((team: any) => {
        const teamMembers = users.filter((user: any) =>
          user.teams?.some((t: any) => t.id === team.id)
        );
        const teamEPs = escalationPolicies.filter((ep: any) =>
          ep.teams?.some((t: any) => t.id === team.id)
        );
        const teamServices = services.filter((service: any) =>
          service.teams?.some((t: any) => t.id === team.id)
        );

        return {
          id: team.id,
          name: team.name,
          member_count: teamMembers.length,
          service_count: teamServices.length,
          health_checks: evaluateTeamHealthChecks(team, teamMembers, teamEPs),
        };
      });

      const newData: MatrixData = {
        services: processedServices,
        teams: processedTeams,
        escalation_policies: processedEPs,
        users: processedUsers,
        schedules: processedSchedules,
        metadata: {
          timestamp: new Date().toISOString(),
          total_health_checks: 0,
          passing: 0,
          warning: 0,
          failing: 0,
        },
      };

      // Calculate metadata
      const allChecks = [
        ...newData.services.flatMap(s => s.health_checks),
        ...newData.teams.flatMap(t => t.health_checks),
        ...newData.escalation_policies.flatMap(ep => ep.health_checks),
        ...newData.users.flatMap(u => u.health_checks),
        ...newData.schedules.flatMap(s => s.health_checks),
      ];

      newData.metadata.total_health_checks = allChecks.length;
      newData.metadata.passing = allChecks.filter(c => c.status === 'pass').length;
      newData.metadata.warning = allChecks.filter(c => c.status === 'warning').length;
      newData.metadata.failing = allChecks.filter(c => c.status === 'fail').length;

      console.log(`Evaluated ${newData.metadata.total_health_checks} health checks`);
      setData(newData);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [app]);

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
        <p>Connecting to Health Check Matrix...</p>
      </div>
    );
  }

  return (
    <MatrixView
      data={data}
      selectedType={selectedType}
      setSelectedType={setSelectedType}
      selectedObject={selectedObject}
      setSelectedObject={setSelectedObject}
      onRefresh={fetchData}
      hostContext={hostContext}
      error={error}
      loading={loading}
    />
  );
}

// Matrix View Component
interface MatrixViewProps {
  data: MatrixData | null;
  selectedType: ObjectType;
  setSelectedType: (type: ObjectType) => void;
  selectedObject: string | null;
  setSelectedObject: (id: string | null) => void;
  onRefresh: () => void;
  hostContext?: McpUiHostContext;
  error: string | null;
  loading: boolean;
}

function MatrixView({
  data,
  selectedType,
  setSelectedType,
  selectedObject,
  setSelectedObject,
  onRefresh,
  hostContext,
  error,
  loading,
}: MatrixViewProps) {
  if (loading || !data) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading health checks from PagerDuty...</p>
      </div>
    );
  }

  const currentObjects = data[selectedType];
  const selectedObjectData = currentObjects?.find((obj) => obj.id === selectedObject);

  return (
    <main
      className="matrix-container"
      style={{
        paddingTop: hostContext?.safeAreaInsets?.top,
        paddingRight: hostContext?.safeAreaInsets?.right,
        paddingBottom: hostContext?.safeAreaInsets?.bottom,
        paddingLeft: hostContext?.safeAreaInsets?.left,
      }}
    >
      {/* Header */}
      <header className="matrix-header">
        <div>
          <h1>🏥 PagerDuty Health Check Matrix</h1>
          <div className="health-summary">
            <span className="health-stat healthy">
              ✅ {data.metadata.passing} Passing
            </span>
            <span className="health-stat warning">
              ⚠️ {data.metadata.warning} Warning
            </span>
            <span className="health-stat critical">
              ❌ {data.metadata.failing} Failing
            </span>
            <span className="health-stat total">
              🔍 {data.metadata.total_health_checks} Total Checks
            </span>
          </div>
        </div>
        <button className="refresh-btn" onClick={onRefresh} disabled={loading}>
          🔄 Refresh
        </button>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Object Type Tabs */}
      <div className="object-type-tabs">
        {(["services", "teams", "escalation_policies", "users", "schedules"] as ObjectType[]).map((type) => (
          <button
            key={type}
            className={`tab-button ${selectedType === type ? "active" : ""}`}
            onClick={() => {
              setSelectedType(type);
              setSelectedObject(null);
            }}
          >
            {getObjectTypeLabel(type)}
            <span className="count">({data[type].length})</span>
          </button>
        ))}
      </div>

      {/* Object Grid */}
      <div className="service-grid">
        {currentObjects?.map((obj) => (
          <ObjectCard
            key={obj.id}
            object={obj}
            objectType={selectedType}
            isSelected={selectedObject === obj.id}
            onSelect={() => setSelectedObject(obj.id)}
          />
        ))}
      </div>

      {/* Detail Panel */}
      {selectedObjectData && (
        <div className="detail-panel">
          <button
            className="close-btn"
            onClick={() => setSelectedObject(null)}
          >
            ✕
          </button>
          <h2>{selectedObjectData.name}</h2>

          <div className="detail-section">
            <h3>Health Checks ({selectedObjectData.health_checks.length})</h3>
            <div className="health-checks-list">
              {selectedObjectData.health_checks.map((check) => (
                <div key={check.id} className={`health-check-item status-${check.status}`}>
                  <div className="check-header">
                    <span className="check-status">{getStatusEmoji(check.status)}</span>
                    <span className="check-id">{check.id}</span>
                    <span
                      className="check-severity"
                      style={{ backgroundColor: getSeverityColor(check.severity) }}
                    >
                      {check.severity}
                    </span>
                  </div>
                  <div className="check-values">
                    <span className="current-value">
                      Current: <strong>{check.current_value}</strong>
                    </span>
                    <span className="expected-value">
                      Expected: <strong>{check.expected_value}</strong>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

// Object Card Component
interface ObjectCardProps {
  object: PdObject;
  objectType: ObjectType;
  isSelected: boolean;
  onSelect: () => void;
}

function ObjectCard({ object, isSelected, onSelect }: ObjectCardProps) {
  const passingChecks = object.health_checks.filter((c) => c.status === "pass").length;
  const warningChecks = object.health_checks.filter((c) => c.status === "warning").length;
  const failingChecks = object.health_checks.filter((c) => c.status === "fail").length;
  const totalChecks = object.health_checks.length;

  const overallStatus =
    failingChecks > 0 ? "fail" : warningChecks > 0 ? "warning" : "pass";

  return (
    <div
      className={`service-card status-${overallStatus} ${isSelected ? "selected" : ""}`}
      onClick={onSelect}
    >
      {/* Health Indicator */}
      <div
        className="health-indicator"
        style={{ background: getStatusColor(overallStatus) }}
      >
        <span className="health-emoji">{getStatusEmoji(overallStatus)}</span>
        <span className="health-score">
          {passingChecks}/{totalChecks}
        </span>
      </div>

      {/* Object Info */}
      <div className="service-info">
        <h3 className="service-name">{object.name}</h3>
        {object.teams && (
          <span className="service-team">{object.teams.join(", ")}</span>
        )}
        {object.team && (
          <span className="service-team">{object.team}</span>
        )}
        {object.member_count !== undefined && (
          <span className="service-team">{object.member_count} members</span>
        )}
        {object.service_count !== undefined && (
          <span className="service-team">{object.service_count} services</span>
        )}
      </div>

      {/* Health Check Badge */}
      <div className="incident-badge">
        {failingChecks > 0 && (
          <span className="high-urgency-badge">
            ❌ {failingChecks} failing
          </span>
        )}
        {warningChecks > 0 && (
          <span className="warning-badge">
            ⚠️ {warningChecks} warning
          </span>
        )}
        {passingChecks === totalChecks && (
          <span className="no-incidents">✅ All checks passing</span>
        )}
      </div>
    </div>
  );
}

// Render
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <HealthCheckMatrix />
  </StrictMode>,
);
