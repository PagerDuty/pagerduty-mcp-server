import type { ScheduleUser } from "../api";

interface CoverageUserCardProps {
  user: ScheduleUser;
  onSelect: () => void;
}

function initials(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function CoverageUserCard({ user, onSelect }: CoverageUserCardProps) {
  return (
    <div className="coverage-user-card">
      <div className="coverage-user-avatar">{initials(user.name)}</div>
      <div className="coverage-user-info">
        <div className="coverage-user-name">{user.name}</div>
        <div className="coverage-user-email">{user.email}</div>
      </div>
      <button className="btn btn-primary btn-sm" onClick={onSelect}>
        Select
      </button>
    </div>
  );
}
