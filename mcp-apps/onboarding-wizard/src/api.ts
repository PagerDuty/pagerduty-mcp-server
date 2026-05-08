import type { App } from "@modelcontextprotocol/ext-apps";
import type {
  AlertGroupingFormData,
  CreatedResource,
  EscalationPolicyFormData,
  ScheduleFormData,
  ServiceFormData,
  TeamFormData,
  UserFormData,
} from "./types.js";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";

async function call(app: App, tool: string, args: Record<string, unknown>): Promise<unknown> {
  const result = await app.callServerTool({ name: tool, arguments: args });
  const text = result.content.find((c: { type: string }) => c.type === "text") as { text: string } | undefined;
  if (!text) throw new Error(`No text content from ${tool}`);
  let parsed: unknown;
  try {
    parsed = JSON.parse(text.text);
  } catch {
    // FastMCP error messages are plain text, not JSON
    throw new Error(text.text);
  }
  return parsed;
}

export async function fetchCurrentUser(app: App): Promise<{ id: string; name: string }> {
  if (MOCK_MODE) return { id: "CU001", name: "Current User" };
  const data = await call(app, "get_user_data", {}) as { id: string; name: string };
  return data;
}

export async function fetchExistingUsers(app: App): Promise<Array<{ id: string; name: string; email: string }>> {
  if (MOCK_MODE) {
    const { MOCK_USERS } = await import("./mock.js");
    return MOCK_USERS;
  }
  const data = await call(app, "list_users", { query_model: { limit: 100 } }) as { response: Array<{ id: string; name: string; email: string }> };
  return data.response ?? [];
}

export async function fetchExistingSchedules(app: App): Promise<Array<{ id: string; name: string }>> {
  if (MOCK_MODE) {
    const { MOCK_SCHEDULES } = await import("./mock.js");
    return MOCK_SCHEDULES;
  }
  const data = await call(app, "list_schedules", { query_model: { limit: 100 } }) as { response: Array<{ id: string; name: string }> };
  return data.response ?? [];
}

export async function fetchExistingEscalationPolicies(app: App): Promise<Array<{ id: string; name: string }>> {
  if (MOCK_MODE) {
    const { MOCK_ESCALATION_POLICIES } = await import("./mock.js");
    return MOCK_ESCALATION_POLICIES;
  }
  const data = await call(app, "list_escalation_policies", { query_model: { limit: 100 } }) as { response: Array<{ id: string; name: string }> };
  return data.response ?? [];
}

export async function fetchExistingServices(app: App): Promise<Array<{ id: string; name: string }>> {
  if (MOCK_MODE) {
    const { MOCK_SERVICES } = await import("./mock.js");
    return MOCK_SERVICES;
  }
  const data = await call(app, "list_services", { query_model: { limit: 100 } }) as { response: Array<{ id: string; name: string }> };
  return data.response ?? [];
}

export async function createTeam(app: App, form: TeamFormData): Promise<CreatedResource> {
  if (MOCK_MODE) {
    return { type: "Team", name: form.name, id: "T_MOCK_" + Date.now(), status: "success" };
  }
  try {
    // Python: create_team(create_model: TeamCreateRequest)
    // TeamCreateRequest { team: TeamCreate { name, description, default_role? } }
    const data = await call(app, "create_team", {
      create_model: { team: { name: form.name, description: form.description || null } },
    }) as { id: string; name: string };
    return { type: "Team", name: data.name, id: data.id, status: "success" };
  } catch (e) {
    return { type: "Team", name: form.name, id: "", status: "error", error: String(e) };
  }
}

export async function createUser(app: App, form: UserFormData): Promise<CreatedResource> {
  if (MOCK_MODE) {
    return { type: "User", name: form.name, id: "U_MOCK_" + Date.now(), status: "success" };
  }
  try {
    // Python: create_user(request: CreateUserRequest)
    const data = await call(app, "create_user", {
      request: { name: form.name, email: form.email, role: form.role, time_zone: form.time_zone },
    }) as { id: string; name: string };
    return { type: "User", name: data.name, id: data.id, status: "success" };
  } catch (e) {
    return { type: "User", name: form.name, id: "", status: "error", error: String(e) };
  }
}

export async function createSchedule(app: App, form: ScheduleFormData): Promise<CreatedResource> {
  if (MOCK_MODE) {
    return { type: "Schedule", name: form.name, id: "S_MOCK_" + Date.now(), status: "success" };
  }
  try {
    const now = new Date().toISOString();
    // Python: create_schedule(create_model: ScheduleCreateRequest)
    // ScheduleCreateRequest { schedule: ScheduleCreateData }
    // ScheduleLayerCreate { name, start: datetime, rotation_virtual_start: datetime,
    //                       rotation_turn_length_seconds: int, users: [{user: {id, type}}] }
    const layers = form.layers.map((l) => ({
      name: l.name,
      start: now,
      rotation_virtual_start: now,
      rotation_turn_length_seconds: l.rotation_turn_length_seconds,
      users: l.user_ids.map((id) => ({ user: { id, type: "user_reference" } })),
    }));
    const data = await call(app, "create_schedule", {
      create_model: {
        schedule: { name: form.name, time_zone: form.time_zone, schedule_layers: layers },
      },
    }) as { id: string; name: string };
    return { type: "Schedule", name: data.name, id: data.id, status: "success" };
  } catch (e) {
    return { type: "Schedule", name: form.name, id: "", status: "error", error: String(e) };
  }
}

export async function createEscalationPolicy(app: App, form: EscalationPolicyFormData): Promise<CreatedResource> {
  if (MOCK_MODE) {
    return { type: "Escalation Policy", name: form.name, id: "EP_MOCK_" + Date.now(), status: "success" };
  }
  try {
    // Python: create_escalation_policy(escalation_policy: EscalationPolicyCreate)
    // EscalationPolicyCreate { name, description?, num_loops, escalation_rules: EscalationRule[] }
    // EscalationRule { escalation_delay_in_minutes, targets: [{ id, type }] }
    const rules = form.rules.map((r) => ({
      escalation_delay_in_minutes: r.escalation_delay_in_minutes,
      targets: [{ id: r.target_id, type: r.target_type === "user" ? "user_reference" : "schedule_reference" }],
    }));
    const data = await call(app, "create_escalation_policy", {
      escalation_policy: {
        name: form.name,
        description: form.description || null,
        num_loops: form.num_loops,
        escalation_rules: rules,
      },
    }) as { id: string; name: string };
    return { type: "Escalation Policy", name: data.name, id: data.id, status: "success" };
  } catch (e) {
    return { type: "Escalation Policy", name: form.name, id: "", status: "error", error: String(e) };
  }
}

export async function createService(app: App, form: ServiceFormData): Promise<CreatedResource> {
  if (MOCK_MODE) {
    return { type: "Service", name: form.name, id: "SVC_MOCK_" + Date.now(), status: "success" };
  }
  try {
    // Python: create_service(service_data: ServiceCreate)
    // ServiceCreate { service: Service { name, description?, escalation_policy: EscalationPolicyReference } }
    // EscalationPolicyReference { id, type: "escalation_policy_reference" }
    const data = await call(app, "create_service", {
      service_data: {
        service: {
          name: form.name,
          description: form.description || null,
          escalation_policy: { id: form.escalation_policy_id, summary: form.escalation_policy_name, type: "escalation_policy_reference" },
        },
      },
    }) as { id: string; name: string };
    return { type: "Service", name: data.name ?? form.name, id: data.id ?? "", status: "success" };
  } catch (e) {
    return { type: "Service", name: form.name, id: "", status: "error", error: String(e) };
  }
}

export async function createAlertGroupingSetting(app: App, form: AlertGroupingFormData): Promise<CreatedResource> {
  if (MOCK_MODE) {
    return { type: "Alert Grouping", name: `Grouping for ${form.service_id}`, id: "AG_MOCK_" + Date.now(), status: "success" };
  }
  try {
    const config = form.type === "time"
      ? { timeout: form.timeout ?? 300 }
      : form.type === "intelligent"
      ? { time_window: form.timeout ?? 300 }
      : { aggregate: "any", fields: ["summary"], time_window: form.timeout ?? 300 };

    // Python: create_alert_grouping_setting(create_model: AlertGroupingSettingCreateRequest)
    // AlertGroupingSettingCreateRequest { alert_grouping_setting: AlertGroupingSettingCreate }
    const data = await call(app, "create_alert_grouping_setting", {
      create_model: {
        alert_grouping_setting: {
          name: `Alert Grouping for service ${form.service_id}`,
          type: form.type,
          services: [{ id: form.service_id, type: "service_reference" }],
          config,
        },
      },
    }) as { id: string; name: string };
    return { type: "Alert Grouping", name: data.name, id: data.id, status: "success" };
  } catch (e) {
    return { type: "Alert Grouping", name: `Grouping for ${form.service_id}`, id: "", status: "error", error: String(e) };
  }
}
