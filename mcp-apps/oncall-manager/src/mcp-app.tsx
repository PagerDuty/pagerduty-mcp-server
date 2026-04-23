import { useApp } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { fetchAllOnCalls, fetchCurrentUser, fetchSchedules, fetchUserShifts } from "./api";
import type { CurrentUser, OnCallShift, Override, Schedule } from "./api";
import { MyOnCalls } from "./components/MyOnCalls";
import { OverridesTab } from "./components/OverridesTab";
import "./styles.css";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";
type Tab = "myoncalls" | "overrides";

function App() {
  const app = useApp();

  const [tab, setTab] = useState<Tab>("myoncalls");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [myShifts, setMyShifts] = useState<OnCallShift[]>([]);
  const [allShifts, setAllShifts] = useState<OnCallShift[]>([]);
  const [overrides, setOverrides] = useState<Override[]>([]);

  async function loadData() {
    setLoading(true);
    setError(null);
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

      // In mock mode, load mock overrides
      if (MOCK_MODE) {
        const { MOCK_ONCALL_DATA } = await import("./mock");
        setOverrides(MOCK_ONCALL_DATA.overrides);
      }
    } catch (e: any) {
      setError(e?.message ?? "Failed to load data");
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
        <div className="empty-state" style={{ marginTop: 80 }}>
          Waiting for MCP connection…
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="app-header">
        <span className="dot">●</span>
        <h1>On-Call Manager</h1>
        <div className="tabs">
          <button
            className={`tab-btn ${tab === "myoncalls" ? "active" : ""}`}
            onClick={() => setTab("myoncalls")}
          >
            My On-Calls
          </button>
          <button
            className={`tab-btn ${tab === "overrides" ? "active" : ""}`}
            onClick={() => setTab("overrides")}
          >
            Overrides
          </button>
        </div>
      </div>

      <div className="tab-content">
        {loading && (
          <div className="loading-row">
            <span className="spinner" />
            Loading schedule data…
          </div>
        )}

        {!loading && error && (
          <p className="error-banner">{error}</p>
        )}

        {!loading && !error && currentUser && (
          <>
            {tab === "myoncalls" && (
              <MyOnCalls
                app={app ?? ({} as any)}
                currentUser={currentUser}
                myShifts={myShifts}
                allShifts={allShifts}
                schedules={schedules}
                onOverrideCreated={loadData}
              />
            )}
            {tab === "overrides" && (
              <OverridesTab
                app={app ?? ({} as any)}
                schedules={schedules}
                overrides={overrides}
                myShifts={myShifts}
                onOverrideCreated={loadData}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function McpApp() {
  return <App />;
}

// MCP app bootstrap — file must export default component
const rootEl = document.getElementById("root");
if (rootEl) {
  import("react-dom/client").then(({ createRoot }) => {
    createRoot(rootEl).render(<McpApp />);
  });
}
