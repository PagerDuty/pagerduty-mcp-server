import { useState } from "react";
import { BestPracticesPanel } from "./BestPracticesPanel.js";
import type { TeamMemberAssignment, TeamMembershipFormData } from "../types.js";

interface Props {
  memberships: TeamMembershipFormData[];
  wizardTeams: Array<{ id: string; name: string }>;
  availableUsers: Array<{ id: string; name: string; email: string }>;
  onChange: (memberships: TeamMembershipFormData[]) => void;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const ROLES: Array<{ value: TeamMemberAssignment["role"]; label: string; hint: string }> = [
  { value: "manager",   label: "Manager",   hint: "Configures team settings, schedules, services" },
  { value: "responder", label: "Responder",  hint: "Responds to incidents, can be on-call" },
  { value: "observer",  label: "Observer",   hint: "View-only; good for new hires & stakeholders" },
];

const MEMBERSHIP_TIPS = [
  { icon: "🔑", text: "Every team needs at least 1 Manager and should have 2–5 Responders." },
  { icon: "🎯", text: "Responders get paged on-call. Managers configure schedules and services. Observers watch and learn without getting paged." },
  { icon: "🆕", text: "New hires: assign as Observer for their first 1–2 weeks, then promote to Responder once they're ready." },
  { icon: "🏢", text: "All users must belong to at least one team — unassigned users have view-only access and can't make changes." },
];

export function PhaseTeamMembership({
  memberships,
  wizardTeams,
  availableUsers,
  onChange,
  onNext,
  onBack,
  onSkip,
}: Props) {
  const [addingTo, setAddingTo] = useState<string | null>(null);
  const [draftUserId, setDraftUserId] = useState("");
  const [draftRole, setDraftRole] = useState<TeamMemberAssignment["role"]>("responder");

  // Ensure every wizard team has an entry
  const ensured: TeamMembershipFormData[] = wizardTeams.map((t) => {
    const existing = memberships.find((m) => m.team_id === t.id);
    return existing ?? { team_id: t.id, team_name: t.name, members: [] };
  });

  function save(updated: TeamMembershipFormData[]) {
    onChange(updated);
  }

  function addMember(teamId: string) {
    if (!draftUserId) return;
    const user = availableUsers.find((u) => u.id === draftUserId);
    if (!user) return;
    const updated = ensured.map((m) => {
      if (m.team_id !== teamId) return m;
      // prevent duplicate
      if (m.members.some((x) => x.user_id === draftUserId)) return m;
      return {
        ...m,
        members: [...m.members, { user_id: draftUserId, user_name: user.name, role: draftRole }],
      };
    });
    save(updated);
    setDraftUserId("");
    setDraftRole("responder");
    setAddingTo(null);
  }

  function removeMember(teamId: string, userId: string) {
    const updated = ensured.map((m) =>
      m.team_id === teamId
        ? { ...m, members: m.members.filter((x) => x.user_id !== userId) }
        : m
    );
    save(updated);
  }

  function updateRole(teamId: string, userId: string, role: TeamMemberAssignment["role"]) {
    const updated = ensured.map((m) =>
      m.team_id === teamId
        ? { ...m, members: m.members.map((x) => x.user_id === userId ? { ...x, role } : x) }
        : m
    );
    save(updated);
  }

  const totalAssigned = ensured.reduce((acc, m) => acc + m.members.length, 0);

  if (wizardTeams.length === 0) {
    return (
      <div className="phase-container">
        <div className="phase-header">
          <h2>Team Membership</h2>
          <p>Assign users to teams with their roles.</p>
        </div>
        <p style={{ color: "var(--color-text-muted)", fontSize: 14 }}>
          No teams were created in this wizard session. Skip this phase or go back to add teams first.
        </p>
        <div className="nav-bar">
          <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
          <div className="nav-bar-right">
            <button className="btn btn-secondary" onClick={onBack}>← Back</button>
            <button className="btn btn-primary" onClick={onNext}>Next →</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="phase-container">
      <div className="phase-header">
        <h2>Team Membership</h2>
        <p>Assign users to teams and set their role within each team.</p>
      </div>

      <BestPracticesPanel phase="Team Membership" tips={MEMBERSHIP_TIPS} />

      <div className="membership-teams">
        {ensured.map((m) => {
          const unassigned = availableUsers.filter(
            (u) => !m.members.some((x) => x.user_id === u.id)
          );
          const isAdding = addingTo === m.team_id;

          return (
            <div key={m.team_id} className="membership-team-card">
              <div className="membership-team-header">
                <span className="membership-team-name">{m.team_name}</span>
                <span className="membership-team-count">
                  {m.members.length} member{m.members.length !== 1 ? "s" : ""}
                </span>
              </div>

              {m.members.length > 0 && (
                <div className="membership-member-list">
                  {m.members.map((member) => (
                    <div key={member.user_id} className="membership-member-row">
                      <span className="membership-member-name">{member.user_name}</span>
                      <select
                        className="membership-role-select"
                        value={member.role}
                        onChange={(e) =>
                          updateRole(m.team_id, member.user_id, (e.target as HTMLSelectElement).value as TeamMemberAssignment["role"])
                        }
                      >
                        {ROLES.map((r) => (
                          <option key={r.value} value={r.value}>{r.label}</option>
                        ))}
                      </select>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => removeMember(m.team_id, member.user_id)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {isAdding ? (
                <div className="membership-add-row">
                  <select
                    className="membership-user-select"
                    value={draftUserId}
                    onChange={(e) => setDraftUserId((e.target as HTMLSelectElement).value)}
                  >
                    <option value="">— pick a user —</option>
                    {unassigned.map((u) => (
                      <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                    ))}
                  </select>
                  <select
                    className="membership-role-select"
                    value={draftRole}
                    onChange={(e) => setDraftRole((e.target as HTMLSelectElement).value as TeamMemberAssignment["role"])}
                  >
                    {ROLES.map((r) => (
                      <option key={r.value} value={r.value} title={r.hint}>{r.label}</option>
                    ))}
                  </select>
                  <button
                    className="btn btn-primary btn-sm"
                    disabled={!draftUserId}
                    onClick={() => addMember(m.team_id)}
                  >
                    Add
                  </button>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => { setAddingTo(null); setDraftUserId(""); }}
                  >
                    Cancel
                  </button>
                </div>
              ) : unassigned.length > 0 ? (
                <button
                  className="btn btn-secondary btn-sm membership-add-btn"
                  onClick={() => { setAddingTo(m.team_id); setDraftUserId(""); setDraftRole("responder"); }}
                >
                  + Add member
                </button>
              ) : (
                <span className="membership-all-assigned">All available users assigned</span>
              )}
            </div>
          );
        })}
      </div>

      <div className="nav-bar">
        <button className="skip-btn" onClick={onSkip}>Skip this phase</button>
        <div className="nav-bar-right">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button
            className="btn btn-primary"
            onClick={onNext}
            disabled={totalAssigned === 0}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
