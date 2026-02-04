/**
 * Centralized API functions for calling existing PagerDuty MCP tools
 *
 * This module calls the EXISTING tools directly instead of wrapper tools.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

export interface FilterOptions {
  status: string[];
  urgency: string[];
  auto_refresh: boolean;
}

export interface IncidentData {
  incidents: any[];
  filters: FilterOptions;
  metadata: {
    timestamp: string;
    total_count: number;
  };
}

export interface IncidentDetails {
  incident: any;
  notes: any[];
  alerts: any[];
  changes: any[];
}

export interface SimilarIncidentsData {
  past_incidents: any[];
  related_incidents: any[];
}

/**
 * Extract JSON data from MCP tool result
 */
function extractData<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

/**
 * Fetch incidents list using the existing list_incidents tool
 */
export async function fetchIncidents(
  app: App,
  filters: FilterOptions
): Promise<IncidentData | null> {
  try {
    console.log("[API] Calling list_incidents with:", filters);

    const result = await app.callServerTool({
      name: "list_incidents",
      arguments: {
        query_model: {
          status: filters.status,
          urgencies: filters.urgency.length > 0 ? filters.urgency : undefined,
          limit: 100,
        },
      },
    });

    console.log("[API] Raw tool result:", result);
    console.log("[API] isError:", result.isError);
    console.log("[API] content:", result.content);

    // Check for errors first
    if (result.isError) {
      const errorText = result.content?.find((c) => c.type === "text")?.text;
      console.error("[API] Tool returned error:", errorText);
      return null;
    }

    const rawData = extractData<any>(result);
    console.log("[API] Extracted data:", rawData);
    console.log("[API] rawData.response:", rawData?.response);
    console.log("[API] rawData.response length:", rawData?.response?.length);

    if (!rawData) {
      console.error("[API] No data extracted from result");
      return null;
    }

    // Transform the API response to match our UI format
    const transformed = {
      incidents: rawData.response || rawData.incidents || [],
      filters,
      metadata: {
        timestamp: new Date().toISOString(),
        total_count: (rawData.response || rawData.incidents || []).length,
      },
    };

    console.log("[API] Transformed data:", transformed);
    console.log("[API] Incident count:", transformed.incidents.length);

    return transformed;
  } catch (error) {
    console.error("[API] Failed to fetch incidents:", error);
    console.error("[API] Error details:", error);
    throw error;
  }
}

/**
 * Fetch comprehensive incident details using multiple existing tools
 */
export async function fetchIncidentDetails(
  app: App,
  incidentId: string
): Promise<IncidentDetails | null> {
  try {
    console.log("[API] Fetching details for incident:", incidentId);

    // Call all tools in parallel for efficiency
    const [incidentResult, notesResult, alertsResult, changesResult] = await Promise.all([
      app.callServerTool({ name: "get_incident", arguments: { incident_id: incidentId } }),
      app.callServerTool({ name: "list_incident_notes", arguments: { incident_id: incidentId } }),
      app.callServerTool({
        name: "list_alerts_from_incident",
        arguments: {
          incident_id: incidentId,
          query_model: { limit: 50 }
        }
      }),
      app.callServerTool({
        name: "list_incident_change_events",
        arguments: { incident_id: incidentId }
      }),
    ]);

    const incident = extractData<any>(incidentResult);
    const notes = extractData<any>(notesResult);
    const alerts = extractData<any>(alertsResult);
    const changes = extractData<any>(changesResult);

    console.log("[API] Incident details fetched:", { incident, notes, alerts, changes });

    return {
      incident: incident?.response || incident,
      notes: notes?.response || [],
      alerts: alerts?.response || [],
      changes: changes?.response || [],
    };
  } catch (error) {
    console.error("[API] Failed to fetch incident details:", error);
    throw error;
  }
}

/**
 * Acknowledge an incident using manage_incidents tool
 */
export async function acknowledgeIncident(
  app: App,
  incidentId: string
): Promise<boolean> {
  try {
    console.log("[API] Acknowledging incident:", incidentId);

    await app.callServerTool({
      name: "manage_incidents",
      arguments: {
        manage_request: {
          incident_ids: [incidentId],
          status: "acknowledged",
        },
      },
    });

    return true;
  } catch (error) {
    console.error("[API] Failed to acknowledge incident:", error);
    throw error;
  }
}

/**
 * Resolve an incident using manage_incidents tool
 */
export async function resolveIncident(
  app: App,
  incidentId: string
): Promise<boolean> {
  try {
    console.log("[API] Resolving incident:", incidentId);

    await app.callServerTool({
      name: "manage_incidents",
      arguments: {
        manage_request: {
          incident_ids: [incidentId],
          status: "resolved",
        },
      },
    });

    return true;
  } catch (error) {
    console.error("[API] Failed to resolve incident:", error);
    throw error;
  }
}

/**
 * Escalate an incident using manage_incidents tool
 */
export async function escalateIncident(
  app: App,
  incidentId: string,
  escalation_policy_id: string
): Promise<boolean> {
  try {
    console.log("[API] Escalating incident:", incidentId, "to policy:", escalation_policy_id);

    await app.callServerTool({
      name: "manage_incidents",
      arguments: {
        manage_request: {
          incident_ids: [incidentId],
          escalation_policy_id,
        },
      },
    });

    return true;
  } catch (error) {
    console.error("[API] Failed to escalate incident:", error);
    throw error;
  }
}

/**
 * Add a note to an incident using add_note_to_incident tool
 */
export async function addIncidentNote(
  app: App,
  incidentId: string,
  note: string
): Promise<boolean> {
  try {
    console.log("[API] Adding note to incident:", incidentId);

    await app.callServerTool({
      name: "add_note_to_incident",
      arguments: {
        incident_id: incidentId,
        note: note,
      },
    });

    return true;
  } catch (error) {
    console.error("[API] Failed to add note:", error);
    throw error;
  }
}

/**
 * Fetch similar incidents using get_past_incidents and get_related_incidents tools
 */
export async function fetchSimilarIncidents(
  app: App,
  incidentId: string
): Promise<SimilarIncidentsData | null> {
  try {
    console.log("[API] Fetching similar incidents for:", incidentId);

    // Call both tools in parallel
    const [pastResult, relatedResult] = await Promise.allSettled([
      app.callServerTool({
        name: "get_past_incidents",
        arguments: {
          incident_id: incidentId,
          query_model: {}
        }
      }),
      app.callServerTool({
        name: "get_related_incidents",
        arguments: {
          incident_id: incidentId,
          query_model: {}
        }
      }),
    ]);

    const past_incidents = pastResult.status === "fulfilled"
      ? extractData<any>(pastResult.value)?.response || []
      : [];

    const related_incidents = relatedResult.status === "fulfilled"
      ? extractData<any>(relatedResult.value)?.response || []
      : [];

    console.log("[API] Similar incidents fetched:", { past_incidents, related_incidents });

    return {
      past_incidents,
      related_incidents,
    };
  } catch (error) {
    console.error("[API] Failed to fetch similar incidents:", error);
    throw error;
  }
}

/**
 * Fetch escalation policies using list_escalation_policies tool
 */
export async function fetchEscalationPolicies(app: App): Promise<any[]> {
  try {
    console.log("[API] Fetching escalation policies");

    const result = await app.callServerTool({
      name: "list_escalation_policies",
      arguments: {
        query_model: {}
      },
    });

    const data = extractData<any>(result);
    return data?.response || [];
  } catch (error) {
    console.error("[API] Failed to fetch escalation policies:", error);
    return [];
  }
}

/**
 * Fetch available priorities using list_priorities tool
 */
export async function fetchPriorities(app: App): Promise<any[]> {
  try {
    console.log("[API] Fetching priorities");

    const result = await app.callServerTool({
      name: "list_priorities",
      arguments: {},
    });

    const data = extractData<any>(result);
    return data?.response || [];
  } catch (error) {
    console.error("[API] Failed to fetch priorities:", error);
    return [];
  }
}

/**
 * Change incident priority using manage_incidents tool
 */
export async function changeIncidentPriority(
  app: App,
  incidentId: string,
  priorityId: string
): Promise<boolean> {
  try {
    console.log("[API] Changing incident priority:", incidentId, priorityId);

    await app.callServerTool({
      name: "manage_incidents",
      arguments: {
        manage_request: {
          incident_ids: [incidentId],
          priority: {
            id: priorityId,
            type: "priority_reference"
          },
        },
      },
    });

    return true;
  } catch (error) {
    console.error("[API] Failed to change priority:", error);
    throw error;
  }
}

/**
 * Fetch available incident workflows using list_incident_workflows tool
 */
export async function fetchIncidentWorkflows(app: App): Promise<any[]> {
  try {
    console.log("[API] Fetching incident workflows");

    const result = await app.callServerTool({
      name: "list_incident_workflows",
      arguments: {
        query_model: {}
      },
    });

    const data = extractData<any>(result);
    return data?.response || [];
  } catch (error) {
    console.error("[API] Failed to fetch workflows:", error);
    return [];
  }
}

/**
 * Start an incident workflow using start_incident_workflow tool
 */
export async function startIncidentWorkflow(
  app: App,
  workflowId: string,
  incidentId: string
): Promise<boolean> {
  try {
    console.log("[API] Starting workflow:", workflowId, "for incident:", incidentId);

    await app.callServerTool({
      name: "start_incident_workflow",
      arguments: {
        workflow_id: workflowId,
        instance_request: {
          incident: {
            id: incidentId,
            type: "incident_reference"
          }
        }
      },
    });

    return true;
  } catch (error) {
    console.error("[API] Failed to start workflow:", error);
    throw error;
  }
}
