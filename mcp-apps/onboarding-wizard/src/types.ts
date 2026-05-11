export type Phase =
  | "teams"
  | "users"
  | "team-membership"
  | "schedules"
  | "escalation-policies"
  | "services"
  | "aiops"
  | "incident-workflows"
  | "review";

export interface TeamFormData {
  name: string;
  description: string;
}

export interface UserFormData {
  name: string;
  email: string;
  role: string;
  time_zone: string;
}

export interface ScheduleLayer {
  name: string;
  rotation_turn_length_seconds: number;
  user_ids: string[];
  handoff_time: string;
}

export interface ScheduleFormData {
  name: string;
  time_zone: string;
  layers: ScheduleLayer[];
}

export interface EscalationRule {
  escalation_delay_in_minutes: number;
  target_type: "user" | "schedule";
  target_id: string;
}

export interface EscalationPolicyFormData {
  name: string;
  description: string;
  num_loops: number;
  rules: EscalationRule[];
}

export interface ServiceFormData {
  name: string;
  description: string;
  escalation_policy_id: string;
  escalation_policy_name: string;
}

export interface AlertGroupingFormData {
  service_id: string;
  type: "intelligent" | "time" | "content_based";
  timeout?: number;
}

export interface TeamMemberAssignment {
  user_id: string;
  user_name: string;
  role: "manager" | "responder" | "observer";
}

export interface TeamMembershipFormData {
  team_id: string;   // "new:TeamName" placeholder during wizard, resolved at submit
  team_name: string;
  members: TeamMemberAssignment[];
}

export interface IncidentWorkflowFormData {
  name: string;
  description: string;
}

export interface WizardState {
  teams: TeamFormData[];
  users: UserFormData[];
  teamMemberships: TeamMembershipFormData[];
  schedules: ScheduleFormData[];
  escalationPolicies: EscalationPolicyFormData[];
  services: ServiceFormData[];
  alertGroupings: AlertGroupingFormData[];
  incidentWorkflows: IncidentWorkflowFormData[];
}

export interface CreatedResource {
  type: string;
  name: string;
  id: string;
  status: "success" | "error";
  error?: string;
}

export interface PhaseResult {
  phase: Phase;
  created: CreatedResource[];
}
