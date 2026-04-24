import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { useEffect, useState } from "react";
import { fetchAllOnCalls, fetchCurrentUser, fetchSchedules, fetchUserShifts } from "./api";
import type { CurrentUser, OnCallShift, Schedule } from "./api";
import { EscalationPoliciesModal } from "./components/EscalationPoliciesModal";
import { MyOnCalls } from "./components/MyOnCalls";
import { OverridesModal } from "./components/OverridesModal";
import { SchedulesModal } from "./components/SchedulesModal";
import "./styles.css";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";
type Modal = "myoncalls" | "overrides" | "schedules" | "escalations" | null;

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "On-Call Manager", version: "2.0.0" },
    capabilities: {},
  });

  const [modal, setModal] = useState<Modal>(null);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [myShifts, setMyShifts] = useState<OnCallShift[]>([]);
  const [allShifts, setAllShifts] = useState<OnCallShift[]>([]);

  async function loadData() {
    setLoading(true);
    try {
      const since = new Date().toISOString();
      const until = new Date(Date.now() + 7 * 86_400_000).toISOString();
      const user = await fetchCurrentUser(app ?? ({} as any));
      setCurrentUser(user);
      const [scheds, myS, allS] = await Promise.all([
        fetchSchedules(app ?? ({} as any)),
        user ? fetchUserShifts(app ?? ({} as any), user.id, since, until) : Promise.resolve([]),
        fetchAllOnCalls(app ?? ({} as any), since, until),
      ]);
      setSchedules(scheds);
      setMyShifts(myS);
      setAllShifts(allS);
    } catch {
      // silently fail — cards show counts as 0
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!app && !MOCK_MODE) return;
    loadData();
  }, [app]);

  if (!app && !MOCK_MODE) {
    return (
      <div className="app">
        <div className="app-header">
          <span className="dot">●</span>
          <h1>On-Call Manager</h1>
        </div>
        <div className="empty-state" style={{ marginTop: 80 }}>
          {connectionError ? `Connection error: ${connectionError.message}` : "Waiting for MCP connection…"}
        </div>
      </div>
    );
  }

  const activeNow = myShifts.filter((s) => {
    const now = Date.now();
    return new Date(s.start).getTime() <= now && new Date(s.end).getTime() > now;
  });
  const nextShift = myShifts
    .filter((s) => new Date(s.start).getTime() > Date.now())
    .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())[0];

  function myOnCallsBadge() {
    if (loading) return null;
    if (activeNow.length > 0) return <span className="home-card-badge active">● On-call now</span>;
    if (nextShift) {
      const ms = new Date(nextShift.start).getTime() - Date.now();
      const h = Math.floor(ms / 3_600_000);
      const d = Math.floor(ms / 86_400_000);
      return <span className="home-card-badge info">Next in {d > 0 ? `${d}d` : `${h}h`}</span>;
    }
    return <span className="home-card-badge" style={{ color: "var(--overlay0)" }}>No shifts</span>;
  }

  return (
    <div className="app">
      <div className="app-header">
        <span className="dot">●</span>
        <h1>On-Call Manager</h1>
        {currentUser && <span className="user-chip">{currentUser.name}</span>}
      </div>

      <div className="home-grid">
        <div className="home-card" onClick={() => setModal("myoncalls")}>
          <div className="home-card-icon">📅</div>
          <div className="home-card-title">My On-Calls</div>
          <div className="home-card-desc">View your upcoming shifts and find coverage for any shift.</div>
          {myOnCallsBadge()}
        </div>

        <div className="home-card" onClick={() => setModal("overrides")}>
          <div className="home-card-icon">🔄</div>
          <div className="home-card-title">Overrides</div>
          <div className="home-card-desc">Create, view, and delete schedule overrides across all schedules.</div>
          {!loading && <span className="home-card-badge info">{schedules.length} schedule{schedules.length !== 1 ? "s" : ""}</span>}
        </div>

        <div className="home-card" onClick={() => setModal("schedules")}>
          <div className="home-card-icon">📋</div>
          <div className="home-card-title">Schedules</div>
          <div className="home-card-desc">Browse schedules, view rotation layers, and manage who's on each rotation.</div>
          {!loading && <span className="home-card-badge info">{schedules.length} schedules</span>}
        </div>

        <div className="home-card" onClick={() => setModal("escalations")}>
          <div className="home-card-icon">📊</div>
          <div className="home-card-title">Escalation Policies</div>
          <div className="home-card-desc">View and edit escalation rules — add targets, adjust delays, create new policies.</div>
        </div>
      </div>

      {modal === "myoncalls" && (
        <MyOnCalls
          app={app ?? ({} as any)}
          currentUser={currentUser ?? { id: "", name: "Unknown", email: "" }}
          myShifts={myShifts}
          allShifts={allShifts}
          schedules={schedules}
          onOverrideCreated={loadData}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "overrides" && (
        <OverridesModal
          app={app ?? ({} as any)}
          schedules={schedules}
          myShifts={myShifts}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "schedules" && (
        <SchedulesModal
          app={app ?? ({} as any)}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "escalations" && (
        <EscalationPoliciesModal
          app={app ?? ({} as any)}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}

export default function McpApp() {
  return <App />;
}

const rootEl = document.getElementById("root");
if (rootEl) {
  import("react-dom/client").then(({ createRoot }) => {
    createRoot(rootEl).render(<McpApp />);
  });
}
