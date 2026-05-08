import type { App as McpApp } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { useEffect, useState } from "react";
import { createAlertGroupingSetting, createEscalationPolicy, createSchedule, createService, createTeam, createUser, fetchExistingEscalationPolicies, fetchExistingSchedules, fetchExistingServices, fetchExistingUsers } from "./api.js";
import { PhaseAIOps } from "./components/PhaseAIOps.js";
import { PhaseEscalationPolicies } from "./components/PhaseEscalationPolicies.js";
import { PhaseIncidentWorkflows } from "./components/PhaseIncidentWorkflows.js";
import { PhaseSchedules } from "./components/PhaseSchedules.js";
import { PhaseServices } from "./components/PhaseServices.js";
import { PhaseTeams } from "./components/PhaseTeams.js";
import { PhaseUsers } from "./components/PhaseUsers.js";
import { ReviewSummary } from "./components/ReviewSummary.js";
import { Stepper } from "./components/Stepper.js";
import "./styles.css";
import type { AlertGroupingFormData, CreatedResource, EscalationPolicyFormData, IncidentWorkflowFormData, Phase, PhaseResult, ScheduleFormData, ServiceFormData, TeamFormData, UserFormData, WizardState } from "./types.js";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";

const PHASE_ORDER: Phase[] = [
  "teams",
  "users",
  "schedules",
  "escalation-policies",
  "services",
  "aiops",
  "incident-workflows",
  "review",
];

const EMPTY_STATE: WizardState = {
  teams: [],
  users: [],
  schedules: [],
  escalationPolicies: [],
  services: [],
  alertGroupings: [],
  incidentWorkflows: [],
};

function nextPhase(current: Phase): Phase {
  const idx = PHASE_ORDER.indexOf(current);
  return PHASE_ORDER[Math.min(idx + 1, PHASE_ORDER.length - 1)];
}

function prevPhase(current: Phase): Phase {
  const idx = PHASE_ORDER.indexOf(current);
  return PHASE_ORDER[Math.max(idx - 1, 0)];
}

export function App() {
  const { app } = useApp({
    appInfo: { name: "Onboarding Wizard", version: "1.0.0" },
    capabilities: {},
  });
  const [phase, setPhase] = useState<Phase>("teams");
  const [wizardState, setWizardState] = useState<WizardState>(EMPTY_STATE);
  const [results, setResults] = useState<PhaseResult[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Context loaded from existing PD resources (for selects in later phases)
  const [existingUsers, setExistingUsers] = useState<Array<{ id: string; name: string; email: string }>>([]);
  const [existingSchedules, setExistingSchedules] = useState<Array<{ id: string; name: string }>>([]);
  const [existingEPs, setExistingEPs] = useState<Array<{ id: string; name: string }>>([]);
  const [existingServices, setExistingServices] = useState<Array<{ id: string; name: string }>>([]);

  useEffect(() => {
    if (!app && !MOCK_MODE) return;
    const proxy = app ?? ({} as McpApp);
    fetchExistingUsers(proxy!).then(setExistingUsers).catch(() => {});
    fetchExistingSchedules(proxy!).then(setExistingSchedules).catch(() => {});
    fetchExistingEscalationPolicies(proxy!).then(setExistingEPs).catch(() => {});
    fetchExistingServices(proxy!).then(setExistingServices).catch(() => {});
  }, [app]);

  // Merged lists: existing PD resources + ones added in this wizard session
  const allUsers = [
    ...existingUsers,
    ...wizardState.users.map((u) => ({ id: `new:${u.email}`, name: u.name, email: u.email })),
  ];
  const allSchedules = [
    ...existingSchedules,
    ...wizardState.schedules.map((s) => ({ id: `new:${s.name}`, name: s.name })),
  ];
  const allEPs = [
    ...existingEPs,
    ...wizardState.escalationPolicies.map((ep) => ({ id: `new:${ep.name}`, name: ep.name })),
  ];
  const allServices = [
    ...existingServices,
    ...wizardState.services.map((s) => ({ id: `new:${s.name}`, name: s.name })),
  ];

  async function handleSubmit() {
    if (!app && !MOCK_MODE) return;
    const proxy = app ?? ({} as McpApp);
    setSubmitting(true);
    const allResults: PhaseResult[] = [];

    // Teams
    if (wizardState.teams.length > 0) {
      const created: CreatedResource[] = [];
      for (const t of wizardState.teams) {
        created.push(await createTeam(proxy!, t));
      }
      allResults.push({ phase: "teams", created });
    }

    // Users
    if (wizardState.users.length > 0) {
      const created: CreatedResource[] = [];
      for (const u of wizardState.users) {
        created.push(await createUser(proxy!, u));
      }
      allResults.push({ phase: "users", created });
    }

    // Schedules
    if (wizardState.schedules.length > 0) {
      const created: CreatedResource[] = [];
      for (const s of wizardState.schedules) {
        created.push(await createSchedule(proxy!, s));
      }
      allResults.push({ phase: "schedules", created });
    }

    // Escalation Policies
    if (wizardState.escalationPolicies.length > 0) {
      const created: CreatedResource[] = [];
      for (const ep of wizardState.escalationPolicies) {
        created.push(await createEscalationPolicy(proxy!, ep));
      }
      allResults.push({ phase: "escalation-policies", created });
    }

    // Services
    if (wizardState.services.length > 0) {
      const created: CreatedResource[] = [];
      for (const s of wizardState.services) {
        created.push(await createService(proxy!, s));
      }
      allResults.push({ phase: "services", created });
    }

    // AIOps Alert Groupings
    if (wizardState.alertGroupings.length > 0) {
      const created: CreatedResource[] = [];
      for (const g of wizardState.alertGroupings) {
        created.push(await createAlertGroupingSetting(proxy!, g));
      }
      allResults.push({ phase: "aiops", created });
    }

    // Incident Workflows — note: create_incident_workflow is read-only in PD API;
    // we list existing workflows and show names as placeholders
    if (wizardState.incidentWorkflows.length > 0) {
      const created: CreatedResource[] = wizardState.incidentWorkflows.map((w) => ({
        type: "Incident Workflow",
        name: w.name,
        id: "manual",
        status: "success" as const,
        error: "Incident Workflows must be configured manually via the PagerDuty UI.",
      }));
      allResults.push({ phase: "incident-workflows", created });
    }

    setResults(allResults);
    setSubmitting(false);
    setSubmitted(true);
  }

  const update = <K extends keyof WizardState>(key: K, value: WizardState[K]) =>
    setWizardState((s) => ({ ...s, [key]: value }));

  return (
    <div className="wizard-root">
      <Stepper current={phase} />
      {phase === "teams" && (
        <PhaseTeams
          teams={wizardState.teams}
          onChange={(t: TeamFormData[]) => update("teams", t)}
          onNext={() => setPhase(nextPhase(phase))}
          onSkip={() => setPhase(nextPhase(phase))}
        />
      )}
      {phase === "users" && (
        <PhaseUsers
          users={wizardState.users}
          onChange={(u: UserFormData[]) => update("users", u)}
          onNext={() => setPhase(nextPhase(phase))}
          onBack={() => setPhase(prevPhase(phase))}
          onSkip={() => setPhase(nextPhase(phase))}
        />
      )}
      {phase === "schedules" && (
        <PhaseSchedules
          schedules={wizardState.schedules}
          availableUsers={allUsers}
          onChange={(s: ScheduleFormData[]) => update("schedules", s)}
          onNext={() => setPhase(nextPhase(phase))}
          onBack={() => setPhase(prevPhase(phase))}
          onSkip={() => setPhase(nextPhase(phase))}
        />
      )}
      {phase === "escalation-policies" && (
        <PhaseEscalationPolicies
          policies={wizardState.escalationPolicies}
          availableUsers={allUsers}
          availableSchedules={allSchedules}
          onChange={(ep: EscalationPolicyFormData[]) => update("escalationPolicies", ep)}
          onNext={() => setPhase(nextPhase(phase))}
          onBack={() => setPhase(prevPhase(phase))}
          onSkip={() => setPhase(nextPhase(phase))}
        />
      )}
      {phase === "services" && (
        <PhaseServices
          services={wizardState.services}
          availableEscalationPolicies={allEPs}
          onChange={(s: ServiceFormData[]) => update("services", s)}
          onNext={() => setPhase(nextPhase(phase))}
          onBack={() => setPhase(prevPhase(phase))}
          onSkip={() => setPhase(nextPhase(phase))}
        />
      )}
      {phase === "aiops" && (
        <PhaseAIOps
          groupings={wizardState.alertGroupings}
          availableServices={allServices}
          onChange={(g: AlertGroupingFormData[]) => update("alertGroupings", g)}
          onNext={() => setPhase(nextPhase(phase))}
          onBack={() => setPhase(prevPhase(phase))}
          onSkip={() => setPhase(nextPhase(phase))}
        />
      )}
      {phase === "incident-workflows" && (
        <PhaseIncidentWorkflows
          workflows={wizardState.incidentWorkflows}
          onChange={(w: IncidentWorkflowFormData[]) => update("incidentWorkflows", w)}
          onNext={() => setPhase("review")}
          onBack={() => setPhase(prevPhase(phase))}
          onSkip={() => setPhase("review")}
        />
      )}
      {phase === "review" && (
        <ReviewSummary
          state={wizardState}
          results={results}
          submitting={submitting}
          submitted={submitted}
          onSubmit={handleSubmit}
          onBack={() => setPhase(prevPhase(phase))}
        />
      )}
    </div>
  );
}

const MOUNT_ID = "root";

function mount() {
  const el = document.getElementById(MOUNT_ID);
  if (!el) return;
  import("react-dom/client").then(({ createRoot }) => {
    createRoot(el).render(<App />);
  });
}

mount();
