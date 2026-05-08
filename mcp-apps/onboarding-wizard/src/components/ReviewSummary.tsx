import type { CreatedResource, PhaseResult, WizardState } from "../types.js";

interface Props {
  state: WizardState;
  results: PhaseResult[];
  submitting: boolean;
  submitted: boolean;
  onSubmit: () => void;
  onBack: () => void;
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="review-section">
      <h3>{title}</h3>
      {items.map((item, i) => (
        <div key={i} className="review-item">
          <span className="review-item-name">{item}</span>
        </div>
      ))}
    </div>
  );
}

function ResultSection({ title, resources }: { title: string; resources: CreatedResource[] }) {
  if (resources.length === 0) return null;
  return (
    <div className="review-section">
      <h3>{title}</h3>
      {resources.map((r, i) => (
        <div key={i} className="review-item">
          <span className="review-item-name">{r.name}</span>
          <span className={`badge ${r.status === "success" ? "badge-success" : "badge-error"}`}>
            {r.status === "success" ? `✓ ${r.id}` : `✗ ${r.error ?? "error"}`}
          </span>
        </div>
      ))}
    </div>
  );
}

export function ReviewSummary({ state, results, submitting, submitted, onSubmit, onBack }: Props) {
  const totalItems =
    state.teams.length +
    state.users.length +
    state.schedules.length +
    state.escalationPolicies.length +
    state.services.length +
    state.alertGroupings.length +
    state.incidentWorkflows.length;

  if (submitted) {
    const allResults = results.flatMap((r) => r.created);
    const succeeded = allResults.filter((r) => r.status === "success").length;
    const failed = allResults.filter((r) => r.status === "error").length;

    return (
      <div className="phase-container">
        <div className="phase-header">
          <h2>Setup Complete</h2>
          <p>
            {succeeded} resource{succeeded !== 1 ? "s" : ""} created
            {failed > 0 ? `, ${failed} failed` : ""}.
          </p>
        </div>
        {results.map((pr) => (
          <ResultSection
            key={pr.phase}
            title={pr.phase.charAt(0).toUpperCase() + pr.phase.slice(1)}
            resources={pr.created}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Review & Create</h2>
        <p>You're about to create {totalItems} resource{totalItems !== 1 ? "s" : ""} in PagerDuty.</p>
      </div>

      <Section title="Teams" items={state.teams.map((t) => t.name)} />
      <Section title="Users" items={state.users.map((u) => `${u.name} <${u.email}>`)} />
      <Section title="Schedules" items={state.schedules.map((s) => s.name)} />
      <Section title="Escalation Policies" items={state.escalationPolicies.map((ep) => ep.name)} />
      <Section title="Services" items={state.services.map((s) => s.name)} />
      <Section
        title="AIOps Groupings"
        items={state.alertGroupings.map((g) => `${g.service_id} — ${g.type}`)}
      />
      <Section title="Incident Workflows" items={state.incidentWorkflows.map((w) => w.name)} />

      {totalItems === 0 && (
        <div className="empty-state">
          No resources to create. Go back and add at least one item.
        </div>
      )}

      <div className="nav-bar">
        <button className="btn btn-secondary" onClick={onBack} disabled={submitting}>
          ← Back
        </button>
        <button
          className="btn btn-primary"
          onClick={onSubmit}
          disabled={totalItems === 0 || submitting}
        >
          {submitting ? (
            <>
              <span className="spinner" /> Creating…
            </>
          ) : (
            "Create All Resources"
          )}
        </button>
      </div>
    </div>
  );
}
