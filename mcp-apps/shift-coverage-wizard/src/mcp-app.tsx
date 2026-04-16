/**
 * Shift Coverage Wizard - Main App
 *
 * 3-step wizard:
 *  Step 0 — Date range picker → fetch user's on-call shifts
 *  Step 1 — Select a shift to get coverage for
 *  Step 2 — Pick a coverage user → confirm + create override
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import {
  fetchCurrentUser,
  fetchUserOnCallShifts,
  fetchScheduleUsers,
  createOverride,
  type CurrentUser,
  type OnCallShift,
  type ScheduleUser,
} from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { StepIndicator } from "./components/StepIndicator";
import { ShiftCard } from "./components/ShiftCard";
import { CoverageUserCard } from "./components/CoverageUserCard";
import { ConfirmModal } from "./components/ConfirmModal";

const STEPS = ["Date Range", "Select Shift", "Find Coverage"];

function getDefaultSince(): string {
  const d = new Date();
  return d.toISOString().slice(0, 16); // datetime-local format
}

function getDefaultUntil(): string {
  const d = new Date();
  d.setDate(d.getDate() + 14);
  return d.toISOString().slice(0, 16);
}

// Detect dark mode from host context or system preference
function detectTheme(): "dark" | "light" {
  if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) return "dark";
  return "light";
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Shift Coverage Wizard", version: "1.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [step, setStep] = useState(0);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getDefaultUntil);

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [shifts, setShifts] = useState<OnCallShift[]>([]);
  const [selectedShift, setSelectedShift] = useState<OnCallShift | null>(null);
  const [candidates, setCandidates] = useState<ScheduleUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<ScheduleUser | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Step 0 → 1: fetch user + their shifts
  const handleFindShifts = useCallback(async () => {
    if (!app) return;
    setLoading(true);
    setError(null);
    try {
      const user = await fetchCurrentUser(app);
      if (!user) throw new Error("Could not load your user profile. Check your API token.");
      setCurrentUser(user);
      const found = await fetchUserOnCallShifts(app, user.id, new Date(since).toISOString(), new Date(until).toISOString());
      if (found.length === 0) {
        setError("No on-call shifts found in that date range for your user.");
        setLoading(false);
        return;
      }
      setShifts(found);
      setStep(1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load shifts");
    } finally {
      setLoading(false);
    }
  }, [app, since, until]);

  // Step 1 → 2: load coverage candidates for selected shift
  const handleFindCoverage = useCallback(async () => {
    if (!app || !selectedShift) return;
    setLoading(true);
    setError(null);
    try {
      const users = await fetchScheduleUsers(app, selectedShift.scheduleId);
      // Exclude the current user from candidates
      const filtered = users.filter((u) => u.id !== currentUser?.id);
      if (filtered.length === 0) {
        setError("No other users found on this schedule to cover your shift.");
        setLoading(false);
        return;
      }
      setCandidates(filtered);
      setStep(2);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load coverage candidates");
    } finally {
      setLoading(false);
    }
  }, [app, selectedShift, currentUser]);

  // Confirm override
  const handleConfirm = useCallback(async () => {
    if (!app || !selectedShift || !selectedUser) return;
    setConfirmLoading(true);
    try {
      await createOverride(
        app,
        selectedShift.scheduleId,
        selectedUser.id,
        new Date(since).toISOString(),
        new Date(until).toISOString()
      );
      setConfirmOpen(false);
      setSuccess(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create override");
      setConfirmOpen(false);
    } finally {
      setConfirmLoading(false);
    }
  }, [app, selectedShift, selectedUser, since, until]);

  const displayError = connectionError?.message ?? error;

  return (
    <div className="app">
      <header className="app-header">
        <span className="pd-icon">
          <PagerDutyLogo size={22} />
        </span>
        <h1>Shift Coverage Wizard</h1>
      </header>

      <StepIndicator steps={STEPS} current={step} />

      <main className="step-content">
        {displayError && <div className="error-state">{displayError}</div>}
        {success && (
          <div className="success-banner">
            ✓ Override created for {selectedUser?.name} on "{selectedShift?.scheduleName}"
          </div>
        )}

        {/* Step 0: Date range */}
        {step === 0 && (
          <>
            <div className="step-title">When do you need coverage?</div>
            <div className="date-range">
              <div className="date-field">
                <label>From</label>
                <input
                  type="datetime-local"
                  value={since}
                  onChange={(e) => setSince(e.currentTarget.value)}
                />
              </div>
              <div className="date-field">
                <label>To</label>
                <input
                  type="datetime-local"
                  value={until}
                  onChange={(e) => setUntil(e.currentTarget.value)}
                />
              </div>
            </div>
            <div className="btn-row">
              <button
                className="btn btn-primary"
                onClick={handleFindShifts}
                disabled={loading || !since || !until}
              >
                {loading ? "Loading..." : "Find my shifts →"}
              </button>
            </div>
          </>
        )}

        {/* Step 1: Select shift */}
        {step === 1 && (
          <>
            <div className="step-title">
              Your on-call shifts{currentUser ? ` for ${currentUser.name}` : ""}
            </div>
            <div className="shift-list">
              {shifts.map((s, i) => (
                <ShiftCard
                  key={`${s.scheduleId}-${i}`}
                  shift={s}
                  selected={selectedShift?.scheduleId === s.scheduleId && selectedShift?.start === s.start}
                  onSelect={() => setSelectedShift(s)}
                />
              ))}
            </div>
            <div className="btn-row">
              <button className="btn btn-secondary" onClick={() => { setStep(0); setSelectedShift(null); }}>
                ← Back
              </button>
              <button
                className="btn btn-primary"
                onClick={handleFindCoverage}
                disabled={loading || !selectedShift}
              >
                {loading ? "Loading..." : "Find coverage →"}
              </button>
            </div>
          </>
        )}

        {/* Step 2: Select coverage user */}
        {step === 2 && (
          <>
            <div className="step-title">Who can cover?</div>
            <div className="coverage-list">
              {candidates.map((u) => (
                <CoverageUserCard
                  key={u.id}
                  user={u}
                  onSelect={() => {
                    setSelectedUser(u);
                    setConfirmOpen(true);
                  }}
                />
              ))}
            </div>
            <div className="notice">
              ℹ Reach out via Slack or Teams to confirm availability before creating the override.
            </div>
            <div className="btn-row">
              <button className="btn btn-secondary" onClick={() => { setStep(1); setCandidates([]); setSelectedUser(null); }}>
                ← Back
              </button>
            </div>
          </>
        )}

        {confirmOpen && selectedShift && selectedUser && (
          <ConfirmModal
            scheduleName={selectedShift.scheduleName}
            userName={selectedUser.name}
            start={new Date(since).toISOString()}
            end={new Date(until).toISOString()}
            onConfirm={handleConfirm}
            onCancel={() => setConfirmOpen(false)}
            loading={confirmLoading}
          />
        )}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
