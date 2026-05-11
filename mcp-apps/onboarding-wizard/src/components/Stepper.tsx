import type { Phase } from "../types.js";

const PHASES: { id: Phase; label: string }[] = [
  { id: "teams", label: "Teams" },
  { id: "users", label: "Users" },
  { id: "team-membership", label: "Members" },
  { id: "schedules", label: "Schedules" },
  { id: "escalation-policies", label: "Escalation" },
  { id: "services", label: "Services" },
  { id: "aiops", label: "AIOps" },
  { id: "incident-workflows", label: "Workflows" },
  { id: "review", label: "Review" },
];

const ORDER = PHASES.map((p) => p.id);

interface Props {
  current: Phase;
}

export function Stepper({ current }: Props) {
  const currentIdx = ORDER.indexOf(current);

  return (
    <div className="stepper">
      {PHASES.map((phase, idx) => {
        const state =
          idx < currentIdx ? "done" : idx === currentIdx ? "active" : "idle";
        return (
          <div key={phase.id} className={`step ${state}`}>
            <div className="step-bubble">
              {state === "done" ? "✓" : idx + 1}
            </div>
            <div className="step-label">{phase.label}</div>
          </div>
        );
      })}
    </div>
  );
}
