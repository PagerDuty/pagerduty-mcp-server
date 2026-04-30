# Oncall Compensation & Compliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve `mcp-apps/oncall-compensation` into a four-tab unified app (Compensation · Compliance · Fairness · Settings) with configurable pay rates, compliance caps, and fairness/equity analysis — all derived from the existing PagerDuty data fetch.

**Architecture:** Extend the existing app in-place. Add three pure computation modules (`config.ts`, `compensation.ts`, `compliance.ts`, `fairness.ts`) that derive new metrics from the already-fetched `enrichedRecords`. Add four tab components plus a reusable `InfoIcon`. All settings persist to `localStorage`. No new API calls.

**Tech Stack:** React 18, TypeScript, Vite, `@modelcontextprotocol/ext-apps`, existing `businessHours.ts` for outside-hours data.

---

## File Map

| Status | Path | Responsibility |
|--------|------|----------------|
| NEW | `src/config.ts` | `PayConfig`, `ComplianceConfig`, `FairnessConfig` types + `localStorage` load/save/defaults |
| NEW | `src/compensation.ts` | `computeEstimatedPay(record, payConfig)` pure function |
| NEW | `src/compliance.ts` | `deriveComplianceStatus(record, config)` + `ComplianceRecord` type |
| NEW | `src/fairness.ts` | `computeFairnessData(records, config)` → equity scores + outliers |
| NEW | `src/components/InfoIcon.tsx` | Reusable `<InfoIcon text="..." />` with hover tooltip |
| NEW | `src/components/TabBar.tsx` | Tab navigation component; emits `onTabChange` |
| NEW | `src/components/CompensationTab.tsx` | Wraps existing table/summary; receives `compensatedRecords` |
| NEW | `src/components/ComplianceTab.tsx` | Compliance table with progress bars + status badges |
| NEW | `src/components/FairnessTab.tsx` | Bar chart + outlier cards + team equity table |
| NEW | `src/components/SettingsTab.tsx` | Two-column settings panels; emits config change callbacks |
| MODIFY | `src/api.ts` | Add `estimatedPay: number` to `UserCompensationRecord` (default 0) |
| MODIFY | `src/mcp-app.tsx` | Add tab state + config state + new `useMemo` chains; restructure layout |
| MODIFY | `src/components/SummaryCards.tsx` | Add Est. Pay summary card when `totalEstimatedPay > 0` |
| MODIFY | `src/components/CompensationTable.tsx` | Add `estimatedPay` to `SortKey`, `ALL_COLS`, and `renderCell` |
| MODIFY | `src/styles.css` | Add styles for tabs, compliance bars, fairness chart, settings panels |

---

## Task 1: Add config types and localStorage persistence

**Files:**
- Create: `mcp-apps/oncall-compensation/src/config.ts`

- [ ] **Step 1: Create `config.ts`**

```typescript
// src/config.ts

import { defaultBHConfig } from "./businessHours";
import type { BusinessHoursConfig } from "./businessHours";

export interface PayConfig {
  l1RatePerHour: number;
  l2PlusRatePerHour: number;
  offHoursMultiplier: number;
  weekendMultiplier: number;
  holidayMultiplier: number;
}

export interface ComplianceConfig {
  periodHoursCap: number;
  periodOutsideHoursCap: number;
  nearLimitThreshold: number; // 0–1, e.g. 0.9 = 90%
}

export interface FairnessConfig {
  outlierMultiplier: number;
}

export interface AllSettings {
  pay: PayConfig;
  compliance: ComplianceConfig;
  fairness: FairnessConfig;
  businessHours: BusinessHoursConfig;
}

export function defaultPayConfig(): PayConfig {
  return {
    l1RatePerHour: 20,
    l2PlusRatePerHour: 15,
    offHoursMultiplier: 1.5,
    weekendMultiplier: 2.0,
    holidayMultiplier: 2.5,
  };
}

export function defaultComplianceConfig(): ComplianceConfig {
  return {
    periodHoursCap: 160,
    periodOutsideHoursCap: 60,
    nearLimitThreshold: 0.9,
  };
}

export function defaultFairnessConfig(): FairnessConfig {
  return { outlierMultiplier: 2.0 };
}

export function defaultAllSettings(): AllSettings {
  return {
    pay: defaultPayConfig(),
    compliance: defaultComplianceConfig(),
    fairness: defaultFairnessConfig(),
    businessHours: defaultBHConfig(),
  };
}

const STORAGE_KEY = "oncall-compliance-settings";

function serializeBH(bh: BusinessHoursConfig): object {
  return {
    ...bh,
    workDays: Array.from(bh.workDays),
    holidays: Array.from(bh.holidays).sort(),
  };
}

function deserializeBH(raw: any): BusinessHoursConfig {
  return {
    startHour: Number(raw.startHour ?? 9),
    endHour: Number(raw.endHour ?? 18),
    timezone: String(raw.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone),
    workDays: new Set<number>(Array.isArray(raw.workDays) ? raw.workDays.map(Number) : [1,2,3,4,5]),
    holidays: new Set<string>(Array.isArray(raw.holidays) ? raw.holidays.map(String) : []),
  };
}

export function loadSettings(): AllSettings {
  const defaults = defaultAllSettings();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaults;
    const parsed = JSON.parse(raw);
    return {
      pay: { ...defaults.pay, ...parsed.pay },
      compliance: { ...defaults.compliance, ...parsed.compliance },
      fairness: { ...defaults.fairness, ...parsed.fairness },
      businessHours: parsed.businessHours
        ? deserializeBH(parsed.businessHours)
        : defaults.businessHours,
    };
  } catch {
    return defaults;
  }
}

export function saveSettings(s: AllSettings): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      pay: s.pay,
      compliance: s.compliance,
      fairness: s.fairness,
      businessHours: serializeBH(s.businessHours),
    }),
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-compensation/src/config.ts
git commit -m "feat(compensation): add config types and localStorage persistence"
```

---

## Task 2: Add estimated pay computation

**Files:**
- Create: `mcp-apps/oncall-compensation/src/compensation.ts`

- [ ] **Step 1: Create `compensation.ts`**

```typescript
// src/compensation.ts

import type { UserCompensationRecord } from "./api";
import type { PayConfig } from "./config";

export function computeEstimatedPay(
  r: UserCompensationRecord,
  cfg: PayConfig,
): number {
  // outsideHours = weekendHours + holidayHours + off-hours weekday time
  // insideHours = all scheduled time that is NOT outside
  const insideHours = Math.max(
    0,
    r.scheduledHours - r.outsideHours - r.weekendHours - r.holidayHours,
  );

  const pay =
    insideHours * cfg.l1RatePerHour +
    r.outsideHours * cfg.l1RatePerHour * cfg.offHoursMultiplier +
    r.weekendHours * cfg.l1RatePerHour * cfg.weekendMultiplier +
    r.holidayHours * cfg.l1RatePerHour * cfg.holidayMultiplier +
    r.scheduledHoursL2Plus * cfg.l2PlusRatePerHour;

  return Math.round(pay * 100) / 100;
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-compensation/src/compensation.ts
git commit -m "feat(compensation): add estimated pay computation"
```

---

## Task 3: Add compliance status derivation

**Files:**
- Create: `mcp-apps/oncall-compensation/src/compliance.ts`

- [ ] **Step 1: Create `compliance.ts`**

```typescript
// src/compliance.ts

import type { UserCompensationRecord } from "./api";
import type { ComplianceConfig } from "./config";

export type ComplianceStatus = "ok" | "near" | "over";

export interface ComplianceRecord extends UserCompensationRecord {
  estimatedPay: number;
  complianceStatus: ComplianceStatus;
  hoursCapPct: number;       // scheduledHours / periodHoursCap (0–∞)
  outsideCapPct: number;     // outsideHours / periodOutsideHoursCap (0–∞)
}

export function deriveComplianceRecords(
  records: (UserCompensationRecord & { estimatedPay: number })[],
  cfg: ComplianceConfig,
): ComplianceRecord[] {
  return records.map((r) => {
    const hoursCapPct = cfg.periodHoursCap > 0
      ? r.scheduledHours / cfg.periodHoursCap
      : 0;
    const outsideCapPct = cfg.periodOutsideHoursCap > 0
      ? r.outsideHours / cfg.periodOutsideHoursCap
      : 0;

    let complianceStatus: ComplianceStatus = "ok";
    if (hoursCapPct > 1 || outsideCapPct > 1) {
      complianceStatus = "over";
    } else if (hoursCapPct >= cfg.nearLimitThreshold || outsideCapPct >= cfg.nearLimitThreshold) {
      complianceStatus = "near";
    }

    return { ...r, complianceStatus, hoursCapPct, outsideCapPct };
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-compensation/src/compliance.ts
git commit -m "feat(compensation): add compliance status derivation"
```

---

## Task 4: Add fairness/equity computation

**Files:**
- Create: `mcp-apps/oncall-compensation/src/fairness.ts`

- [ ] **Step 1: Create `fairness.ts`**

```typescript
// src/fairness.ts

import type { UserCompensationRecord } from "./api";
import type { FairnessConfig } from "./config";

export interface TeamFairness {
  teamId: string;
  teamName: string;
  memberCount: number;
  avgHours: number;
  stdDev: number;
  outlierCount: number;
  equityScore: number; // 0–100
}

export interface FairnessData {
  globalAvgHours: number;
  globalStdDev: number;
  globalEquityScore: number;
  outliers: (UserCompensationRecord & { multiplierVsAvg: number })[];
  teams: TeamFairness[];
}

function stdDev(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = values.reduce((s, v) => s + v, 0) / values.length;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
}

function equityScore(mean: number, sd: number): number {
  if (mean === 0) return 100;
  return Math.max(0, Math.min(100, Math.round(100 - (sd / mean) * 100)));
}

export function computeFairnessData(
  records: UserCompensationRecord[],
  cfg: FairnessConfig,
): FairnessData {
  if (records.length === 0) {
    return { globalAvgHours: 0, globalStdDev: 0, globalEquityScore: 100, outliers: [], teams: [] };
  }

  const allHours = records.map((r) => r.scheduledHours);
  const globalAvg = allHours.reduce((s, v) => s + v, 0) / allHours.length;
  const globalSd = stdDev(allHours);

  const outliers = records
    .filter((r) => globalAvg > 0 && r.scheduledHours >= cfg.outlierMultiplier * globalAvg)
    .map((r) => ({
      ...r,
      multiplierVsAvg: globalAvg > 0 ? Math.round((r.scheduledHours / globalAvg) * 10) / 10 : 0,
    }))
    .sort((a, b) => b.scheduledHours - a.scheduledHours);

  // Group by primary teamId
  const teamMap = new Map<string, { name: string; members: UserCompensationRecord[] }>();
  for (const r of records) {
    const tid = r.teamId ?? "__none__";
    const tname = r.teamName ?? "No Team";
    if (!teamMap.has(tid)) teamMap.set(tid, { name: tname, members: [] });
    teamMap.get(tid)!.members.push(r);
  }

  const teams: TeamFairness[] = Array.from(teamMap.entries()).map(([teamId, { name, members }]) => {
    const hours = members.map((m) => m.scheduledHours);
    const avg = hours.reduce((s, v) => s + v, 0) / hours.length;
    const sd = stdDev(hours);
    const outlierCount = members.filter(
      (m) => avg > 0 && m.scheduledHours >= cfg.outlierMultiplier * avg,
    ).length;
    return {
      teamId,
      teamName: name,
      memberCount: members.length,
      avgHours: Math.round(avg * 10) / 10,
      stdDev: Math.round(sd * 10) / 10,
      outlierCount,
      equityScore: equityScore(avg, sd),
    };
  });

  teams.sort((a, b) => a.equityScore - b.equityScore);

  return {
    globalAvgHours: Math.round(globalAvg * 10) / 10,
    globalStdDev: Math.round(globalSd * 10) / 10,
    globalEquityScore: equityScore(globalAvg, globalSd),
    outliers,
    teams,
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-compensation/src/fairness.ts
git commit -m "feat(compensation): add fairness and equity score computation"
```

---

## Task 5: Add `estimatedPay` field to `UserCompensationRecord`

**Files:**
- Modify: `mcp-apps/oncall-compensation/src/api.ts`

- [ ] **Step 1: Add `estimatedPay` to the `UserCompensationRecord` interface**

In `src/api.ts`, add `estimatedPay: number` to the interface (after `uniquePeriodsOutside`):

```typescript
  // Outside business hours metrics — computed in the browser from oncallShifts + config
  // Default to 0; recomputed whenever BusinessHoursConfig changes
  outsideHours: number;
  weekendHours: number;
  holidayHours: number;
  maxConsecutiveOutsideHours: number;
  uniquePeriodsOutside: number;

  // Estimated compensation — computed in the browser from PayConfig
  // Default to 0; recomputed whenever PayConfig changes
  estimatedPay: number;
```

- [ ] **Step 2: Set default `estimatedPay: 0` in the record constructor**

In `fetchCompensationData`, inside the `mergedMap.set(userId, { ... })` call, add `estimatedPay: 0` after `uniquePeriodsOutside: 0`.

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/api.ts
git commit -m "feat(compensation): add estimatedPay field to UserCompensationRecord"
```

---

## Task 6: Create reusable InfoIcon component

**Files:**
- Create: `mcp-apps/oncall-compensation/src/components/InfoIcon.tsx`

- [ ] **Step 1: Create `InfoIcon.tsx`**

```tsx
// src/components/InfoIcon.tsx

interface Props {
  text: string;
}

export function InfoIcon({ text }: Props) {
  return (
    <span className="info-icon" title={text} aria-label={text}>
      ⓘ
    </span>
  );
}
```

- [ ] **Step 2: Add CSS for `.info-icon` in `src/styles.css`**

```css
/* Info icon tooltip */
.info-icon {
  display: inline-block;
  font-size: 11px;
  color: var(--text-muted);
  cursor: help;
  margin-left: 4px;
  line-height: 1;
  vertical-align: middle;
  user-select: none;
}
.info-icon:hover {
  color: var(--text-secondary);
}
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/components/InfoIcon.tsx mcp-apps/oncall-compensation/src/styles.css
git commit -m "feat(compensation): add reusable InfoIcon component"
```

---

## Task 7: Create TabBar component

**Files:**
- Create: `mcp-apps/oncall-compensation/src/components/TabBar.tsx`

- [ ] **Step 1: Create `TabBar.tsx`**

```tsx
// src/components/TabBar.tsx

export type TabId = "compensation" | "compliance" | "fairness" | "settings";

interface Tab {
  id: TabId;
  label: string;
}

const TABS: Tab[] = [
  { id: "compensation", label: "💰 Compensation" },
  { id: "compliance",   label: "🛡 Compliance" },
  { id: "fairness",     label: "⚖ Fairness" },
  { id: "settings",     label: "⚙ Settings" },
];

interface Props {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export function TabBar({ activeTab, onTabChange }: Props) {
  return (
    <div className="tab-bar">
      {TABS.map((t) => (
        <button
          key={t.id}
          className={["tab-btn", activeTab === t.id ? "tab-btn--active" : ""].filter(Boolean).join(" ")}
          onClick={() => onTabChange(t.id)}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Add CSS for tab bar in `src/styles.css`**

```css
/* Tab bar */
.tab-bar {
  display: flex;
  align-items: stretch;
  padding: 0 16px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.tab-btn {
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn--active {
  color: var(--pd-green);
  border-bottom-color: var(--pd-green);
  font-weight: 600;
}
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/components/TabBar.tsx mcp-apps/oncall-compensation/src/styles.css
git commit -m "feat(compensation): add TabBar component"
```

---

## Task 8: Create SettingsTab component

**Files:**
- Create: `mcp-apps/oncall-compensation/src/components/SettingsTab.tsx`

- [ ] **Step 1: Create `SettingsTab.tsx`**

```tsx
// src/components/SettingsTab.tsx

import { useState } from "react";
import type { AllSettings } from "../config";
import { defaultAllSettings } from "../config";
import { BusinessHoursConfig } from "./BusinessHoursConfig";
import { InfoIcon } from "./InfoIcon";

interface Props {
  settings: AllSettings;
  onSave: (s: AllSettings) => void;
}

export function SettingsTab({ settings, onSave }: Props) {
  const [draft, setDraft] = useState<AllSettings>(() => ({
    pay: { ...settings.pay },
    compliance: { ...settings.compliance },
    fairness: { ...settings.fairness },
    businessHours: {
      ...settings.businessHours,
      workDays: new Set(settings.businessHours.workDays),
      holidays: new Set(settings.businessHours.holidays),
    },
  }));

  const setPay = (patch: Partial<AllSettings["pay"]>) =>
    setDraft((d) => ({ ...d, pay: { ...d.pay, ...patch } }));

  const setCompliance = (patch: Partial<AllSettings["compliance"]>) =>
    setDraft((d) => ({ ...d, compliance: { ...d.compliance, ...patch } }));

  const setFairness = (patch: Partial<AllSettings["fairness"]>) =>
    setDraft((d) => ({ ...d, fairness: { ...d.fairness, ...patch } }));

  const handleReset = () => setDraft(defaultAllSettings());

  return (
    <div className="settings-tab">
      <div className="settings-columns">

        {/* Left column */}
        <div className="settings-col">

          {/* Pay Rates */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              💰 Pay Rates
              <InfoIcon text="Estimated pay = (inside-hours × L1 rate) + (outside-hours × L1 rate × off-hours multiplier) + (weekend hrs × L1 rate × weekend multiplier) + (holiday hrs × L1 rate × holiday multiplier) + (L2+ hrs × L2+ rate). This is an estimate only." />
            </h3>
            <div className="settings-grid-2">
              <label className="settings-label">
                L1 (Primary) base rate / hr
                <div className="settings-currency-input">
                  <span className="settings-currency-symbol">$</span>
                  <input
                    type="number"
                    min={0}
                    step={1}
                    value={draft.pay.l1RatePerHour}
                    onChange={(e) => setPay({ l1RatePerHour: Number(e.target.value) })}
                    className="settings-input"
                  />
                </div>
              </label>
              <label className="settings-label">
                L2+ (Secondary) base rate / hr
                <div className="settings-currency-input">
                  <span className="settings-currency-symbol">$</span>
                  <input
                    type="number"
                    min={0}
                    step={1}
                    value={draft.pay.l2PlusRatePerHour}
                    onChange={(e) => setPay({ l2PlusRatePerHour: Number(e.target.value) })}
                    className="settings-input"
                  />
                </div>
              </label>
            </div>
            <div className="settings-label" style={{ marginTop: 10 }}>
              Multipliers
              <InfoIcon text="Applied on top of the L1 base rate. Off-hours = weekday hours outside the business window. Weekend = Sat/Sun. Holiday = dates listed in Business Hours config." />
            </div>
            <div className="settings-grid-3" style={{ marginTop: 6 }}>
              <label className="settings-label">
                Off-Hours ×
                <input
                  type="number"
                  min={1}
                  step={0.1}
                  value={draft.pay.offHoursMultiplier}
                  onChange={(e) => setPay({ offHoursMultiplier: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Weekend ×
                <input
                  type="number"
                  min={1}
                  step={0.1}
                  value={draft.pay.weekendMultiplier}
                  onChange={(e) => setPay({ weekendMultiplier: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Holiday ×
                <input
                  type="number"
                  min={1}
                  step={0.1}
                  value={draft.pay.holidayMultiplier}
                  onChange={(e) => setPay({ holidayMultiplier: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
            </div>
          </section>

          {/* Compliance Caps */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              🛡 Compliance Caps
              <InfoIcon text="Users exceeding these caps are flagged ⚠ OVER CAP in the Compliance tab. The near-limit threshold triggers a ⚡ NEAR warning before the cap is hit. Caps apply to the selected date range." />
            </h3>
            <div className="settings-grid-2">
              <label className="settings-label">
                Period total cap (hrs)
                <InfoIcon text="Maximum total scheduled oncall hours allowed in the selected period." />
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={draft.compliance.periodHoursCap}
                  onChange={(e) => setCompliance({ periodHoursCap: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Period outside-hours cap (hrs)
                <InfoIcon text="Maximum oncall hours outside business hours allowed in the selected period." />
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={draft.compliance.periodOutsideHoursCap}
                  onChange={(e) => setCompliance({ periodOutsideHoursCap: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
            </div>
            <label className="settings-label" style={{ marginTop: 10 }}>
              Near-limit warning threshold
              <InfoIcon text="When a user reaches this % of their cap, they show ⚡ NEAR instead of ✓ OK." />
              <div className="settings-slider-row">
                <input
                  type="range"
                  min={50}
                  max={99}
                  step={1}
                  value={Math.round(draft.compliance.nearLimitThreshold * 100)}
                  onChange={(e) => setCompliance({ nearLimitThreshold: Number(e.target.value) / 100 })}
                  className="settings-slider"
                />
                <span className="settings-slider-value">
                  {Math.round(draft.compliance.nearLimitThreshold * 100)}%
                </span>
              </div>
            </label>
          </section>

        </div>

        {/* Right column */}
        <div className="settings-col">

          {/* Business Hours */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              🕐 Business Hours
              <InfoIcon text="Defines what counts as 'business hours' for outside-hours calculations. Oncall time outside this window on work days is counted as off-hours. Weekends and holidays are always outside hours." />
            </h3>
            <BusinessHoursConfig
              config={draft.businessHours}
              onChange={(bh) => setDraft((d) => ({ ...d, businessHours: bh }))}
              showToggle={false}
            />
          </section>

          {/* Fairness Thresholds */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              ⚖ Fairness Thresholds
              <InfoIcon text="Equity Score = 100 − (std deviation ÷ mean × 100), capped 0–100. A perfectly equal team scores 100. Outliers are users whose scheduled hours exceed the threshold multiple of the team average." />
            </h3>
            <label className="settings-label">
              Outlier threshold (× team average)
              <InfoIcon text="A user is flagged as an outlier when their scheduled hours ≥ this multiple of the team average." />
              <div className="settings-slider-row">
                <input
                  type="range"
                  min={1.5}
                  max={5}
                  step={0.5}
                  value={draft.fairness.outlierMultiplier}
                  onChange={(e) => setFairness({ outlierMultiplier: Number(e.target.value) })}
                  className="settings-slider"
                />
                <span className="settings-slider-value">{draft.fairness.outlierMultiplier}×</span>
              </div>
            </label>
          </section>

          {/* Actions */}
          <div className="settings-actions">
            <button className="btn-settings-reset" onClick={handleReset}>
              Reset to defaults
            </button>
            <button className="btn-settings-save" onClick={() => onSave(draft)}>
              Save Settings
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add Settings CSS to `src/styles.css`**

```css
/* Settings tab */
.settings-tab {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.settings-columns {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.settings-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.settings-section {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  padding: 14px;
}

.settings-section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.settings-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

.settings-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.settings-grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.settings-input {
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  color: var(--text-primary);
  padding: 4px 8px;
  font-size: 12px;
  width: 100%;
  outline: none;
}

.settings-input:focus {
  border-color: var(--border-selected);
}

.settings-currency-input {
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  overflow: hidden;
}

.settings-currency-symbol {
  padding: 4px 6px;
  font-size: 11px;
  color: var(--text-muted);
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-card);
}

.settings-currency-input input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  padding: 4px 8px;
  font-size: 12px;
  width: 100%;
  outline: none;
}

.settings-slider-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.settings-slider {
  flex: 1;
  accent-color: var(--pd-green);
}

.settings-slider-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--pd-green);
  min-width: 36px;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 4px;
}

.btn-settings-reset {
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  color: var(--text-secondary);
  padding: 6px 14px;
  font-size: 12px;
  cursor: pointer;
}

.btn-settings-reset:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.btn-settings-save {
  background: var(--pd-green);
  border: none;
  border-radius: 4px;
  color: #fff;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-settings-save:hover {
  opacity: 0.9;
}
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/components/SettingsTab.tsx mcp-apps/oncall-compensation/src/styles.css
git commit -m "feat(compensation): add SettingsTab component"
```

---

## Task 9: Create CompensationTab component

**Files:**
- Create: `mcp-apps/oncall-compensation/src/components/CompensationTab.tsx`
- Modify: `mcp-apps/oncall-compensation/src/components/SummaryCards.tsx`
- Modify: `mcp-apps/oncall-compensation/src/components/CompensationTable.tsx`

- [ ] **Step 1: Extend `SortKey` in `CompensationTable.tsx` to include `estimatedPay`**

Add `"estimatedPay"` to the `SortKey` union type:

```typescript
export type SortKey =
  | "userName"
  | "scheduledHours"
  | "incidentCount"
  | "highUrgencyCount"
  | "incidentHours"
  | "interruptionRate"
  | "offHourInterruptions"
  | "sleepHourInterruptions"
  | "businessHourInterruptions"
  | "outsideHours"
  | "weekendHours"
  | "holidayHours"
  | "maxConsecutiveOutsideHours"
  | "uniquePeriodsOutside"
  | "estimatedPay";
```

- [ ] **Step 2: Add `estimatedPay` column def to `ALL_COLS` in `CompensationTable.tsx`**

Add after the `uniquePeriodsOutside` entry:

```typescript
  { key: "estimatedPay", label: "Est. Pay", description: "Estimated compensation based on L1/L2+ base rates and off-hours/weekend/holiday multipliers configured in Settings. This is an estimate only.", align: "right", toggleable: true },
```

- [ ] **Step 3: Add `estimatedPay` case to `renderCell` in `CompensationTable.tsx`**

Add after the `uniquePeriodsOutside` case:

```typescript
    case "estimatedPay":
      return (
        <td key={key} className="num-cell est-pay-cell">
          {r.estimatedPay > 0 ? `$${r.estimatedPay.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` : <span style={{ color: "var(--text-muted)" }}>—</span>}
        </td>
      );
```

- [ ] **Step 4: Add `estimatedPay` CSS to `src/styles.css`**

```css
.est-pay-cell {
  color: var(--accent-blue);
  font-weight: 500;
}
```

- [ ] **Step 5: Extend `SummaryCards.tsx` to show total estimated pay**

Add a prop `totalEstimatedPay?: number` and render a card when it's > 0:

```tsx
import type { UserCompensationRecord } from "../api";
import { InfoIcon } from "./InfoIcon";

interface Props {
  records: UserCompensationRecord[];
  totalEstimatedPay?: number;
}

export function SummaryCards({ records, totalEstimatedPay }: Props) {
  const totalUsers = records.length;
  const totalOncallHours = records.reduce((s, r) => s + r.scheduledHours, 0);
  const totalIncidents = records.reduce((s, r) => s + r.incidentCount, 0);
  const avgIncidents = totalUsers > 0 ? totalIncidents / totalUsers : 0;
  const totalOffHourIntrs = records.reduce((s, r) => s + r.offHourInterruptions, 0);
  const totalSleepIntrs = records.reduce((s, r) => s + r.sleepHourInterruptions, 0);
  const totalOutsideHours = records.reduce((s, r) => s + r.outsideHours, 0);
  const totalWeekendHours = records.reduce((s, r) => s + r.weekendHours, 0);
  const totalHolidayHours = records.reduce((s, r) => s + r.holidayHours, 0);
  const hasOutsideData = totalOutsideHours > 0;

  return (
    <div className="summary-cards">
      <div className="summary-card">
        <div className="card-value">{totalUsers}</div>
        <div className="card-label">Users On-Call</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{totalOncallHours.toFixed(0)}h</div>
        <div className="card-label">Total Oncall Hours</div>
      </div>
      <div className="summary-card">
        <div className="card-value">{totalIncidents}</div>
        <div className="card-label">Incidents Responded</div>
        <div className="card-sub">
          {records.reduce((s, r) => s + r.highUrgencyCount, 0)} high ·{" "}
          {records.reduce((s, r) => s + r.lowUrgencyCount, 0)} low
        </div>
      </div>
      <div className="summary-card">
        <div className="card-value">{avgIncidents.toFixed(1)}</div>
        <div className="card-label">Avg Incidents / User</div>
      </div>
      {(totalOffHourIntrs > 0 || totalSleepIntrs > 0) && (
        <div className="summary-card">
          <div className="card-value ooh-value">{totalOffHourIntrs + totalSleepIntrs}</div>
          <div className="card-label">OOH Interruptions</div>
          <div className="card-sub">
            {totalOffHourIntrs} off-hr · {totalSleepIntrs} sleep
          </div>
        </div>
      )}
      {hasOutsideData && (
        <div className="summary-card summary-card--bh">
          <div className="card-value bh-value">{totalOutsideHours.toFixed(1)}h</div>
          <div className="card-label">Outside BH Hours</div>
          <div className="card-sub">
            {totalWeekendHours.toFixed(1)}h wknd
            {totalHolidayHours > 0 ? ` · ${totalHolidayHours.toFixed(1)}h holiday` : ""}
          </div>
        </div>
      )}
      {(totalEstimatedPay ?? 0) > 0 && (
        <div className="summary-card summary-card--pay">
          <div className="card-value pay-value">
            ${(totalEstimatedPay!).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Est. Compensation
            <InfoIcon text="Sum of estimated pay across all visible users, based on L1/L2+ rates and multipliers in Settings. This is an estimate only." />
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Add Est. Pay card CSS to `src/styles.css`**

```css
.summary-card--pay {
  border-color: var(--accent-blue-bg);
}
.pay-value {
  color: var(--accent-blue);
}
```

- [ ] **Step 7: Create `CompensationTab.tsx`**

```tsx
// src/components/CompensationTab.tsx

import type { UserCompensationRecord } from "../api";
import type { SortKey } from "./CompensationTable";
import { CompensationTable } from "./CompensationTable";
import { ColumnPicker } from "./ColumnPicker";
import { SummaryCards } from "./SummaryCards";

interface Props {
  records: UserCompensationRecord[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
  visibleCols: Set<SortKey>;
  onVisibleColsChange: (cols: Set<SortKey>) => void;
  colPickerOpen: boolean;
  onColPickerToggle: () => void;
  onColPickerClose: () => void;
  showSummary: boolean;
  onToggleSummary: () => void;
}

export function CompensationTab({
  records,
  selectedId,
  onSelect,
  sortKey,
  sortDir,
  onSort,
  visibleCols,
  onVisibleColsChange,
  colPickerOpen,
  onColPickerToggle,
  onColPickerClose,
  showSummary,
  onToggleSummary,
}: Props) {
  const totalEstimatedPay = records.reduce((s, r) => s + r.estimatedPay, 0);

  return (
    <div className="compensation-tab">
      <div className="controls">
        <button
          className={["btn-summary-toggle", showSummary ? "active" : ""].filter(Boolean).join(" ")}
          onClick={onToggleSummary}
          title={showSummary ? "Hide summary" : "Show summary"}
        >
          {showSummary ? "▲ Summary" : "▼ Summary"}
        </button>
      </div>

      {showSummary && (
        <div className="summary-strip">
          <SummaryCards records={records} totalEstimatedPay={totalEstimatedPay} />
          <div className="summary-actions">
            <div style={{ position: "relative" }}>
              <button
                className={["btn-col-picker", colPickerOpen ? "active" : ""].filter(Boolean).join(" ")}
                onClick={onColPickerToggle}
                title="Show/hide columns"
              >
                ⊞ Columns
              </button>
              <ColumnPicker
                visibleCols={visibleCols}
                onChange={onVisibleColsChange}
                open={colPickerOpen}
                onClose={onColPickerClose}
              />
            </div>
          </div>
        </div>
      )}

      <div className="table-area">
        <CompensationTable
          records={records}
          selectedId={selectedId}
          onSelect={onSelect}
          sortKey={sortKey}
          sortDir={sortDir}
          onSort={onSort}
          visibleCols={visibleCols}
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 8: Add CompensationTab CSS to `src/styles.css`**

```css
.compensation-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
```

- [ ] **Step 9: Commit**

```bash
git add mcp-apps/oncall-compensation/src/components/CompensationTab.tsx \
  mcp-apps/oncall-compensation/src/components/SummaryCards.tsx \
  mcp-apps/oncall-compensation/src/components/CompensationTable.tsx \
  mcp-apps/oncall-compensation/src/styles.css
git commit -m "feat(compensation): add CompensationTab with Est. Pay column and summary card"
```

---

## Task 10: Create ComplianceTab component

**Files:**
- Create: `mcp-apps/oncall-compensation/src/components/ComplianceTab.tsx`

- [ ] **Step 1: Create `ComplianceTab.tsx`**

```tsx
// src/components/ComplianceTab.tsx

import type { ComplianceRecord } from "../compliance";
import type { ComplianceConfig } from "../config";
import { InfoIcon } from "./InfoIcon";

interface Props {
  records: ComplianceRecord[];
  config: ComplianceConfig;
}

function ProgressBar({ pct, status }: { pct: number; status: "ok" | "near" | "over" }) {
  const fillPct = Math.min(pct * 100, 100);
  const color = status === "over" ? "var(--impacted-high)" : status === "near" ? "var(--ooh-orange)" : "var(--pd-green)";
  return (
    <div className="compliance-bar-wrap">
      <div className="compliance-bar-track">
        <div className="compliance-bar-fill" style={{ width: `${fillPct}%`, background: color }} />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: "ok" | "near" | "over" }) {
  if (status === "over") return <span className="compliance-badge compliance-badge--over">⚠ OVER CAP</span>;
  if (status === "near") return <span className="compliance-badge compliance-badge--near">⚡ NEAR</span>;
  return <span className="compliance-badge compliance-badge--ok">✓ OK</span>;
}

export function ComplianceTab({ records, config }: Props) {
  const overCount = records.filter((r) => r.complianceStatus === "over").length;
  const okCount = records.filter((r) => r.complianceStatus === "ok").length;

  return (
    <div className="compliance-tab">
      {overCount > 0 && (
        <div className="compliance-violation-banner">
          ⚠ <strong>{overCount} user{overCount > 1 ? "s" : ""}</strong> have exceeded configured oncall caps this period.
        </div>
      )}

      <div className="summary-cards" style={{ padding: "8px 16px" }}>
        <div className="summary-card">
          <div className="card-value" style={{ color: "var(--pd-green)" }}>{okCount}</div>
          <div className="card-label">Compliant</div>
          <div className="card-sub">users within caps</div>
        </div>
        <div className="summary-card" style={{ borderColor: overCount > 0 ? "var(--impacted-high-bg)" : undefined }}>
          <div className="card-value" style={{ color: overCount > 0 ? "var(--impacted-high)" : "var(--text-muted)" }}>{overCount}</div>
          <div className="card-label">Violations</div>
          <div className="card-sub">users over cap</div>
        </div>
        <div className="summary-card">
          <div className="card-value">{config.periodHoursCap}h</div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Period Total Cap
            <InfoIcon text="Maximum total scheduled oncall hours per user for the selected date range. Configured in Settings." />
          </div>
        </div>
        <div className="summary-card">
          <div className="card-value">{config.periodOutsideHoursCap}h</div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Outside-Hours Cap
            <InfoIcon text="Maximum oncall hours outside business hours per user for the selected date range. Configured in Settings." />
          </div>
        </div>
      </div>

      <div className="table-area">
        <table className="comp-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Team</th>
              <th className="sortable" style={{ textAlign: "right" }}>Sched Hours</th>
              <th>
                vs. Period Cap
                <InfoIcon text={`Cap: ${config.periodHoursCap}h. Progress bar shows usage. Red = over cap, amber = within ${Math.round(config.nearLimitThreshold * 100)}% of cap.`} />
              </th>
              <th style={{ textAlign: "right" }}>Outside Hrs</th>
              <th>
                vs. Outside Cap
                <InfoIcon text={`Cap: ${config.periodOutsideHoursCap}h. Red = over cap, amber = within ${Math.round(config.nearLimitThreshold * 100)}% of cap.`} />
              </th>
              <th style={{ textAlign: "center" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.userId} className={r.complianceStatus === "over" ? "compliance-row--over" : ""}>
                <td>{r.userName}</td>
                <td style={{ color: "var(--text-muted)" }}>{r.teamName ?? "—"}</td>
                <td className="num-cell" style={{ color: r.complianceStatus === "over" ? "var(--impacted-high)" : undefined }}>
                  {r.scheduledHours.toFixed(1)}h
                </td>
                <td>
                  <ProgressBar pct={r.hoursCapPct} status={r.complianceStatus} />
                  <div className="compliance-bar-label">
                    {r.scheduledHours.toFixed(1)}/{config.periodHoursCap}h
                    {r.hoursCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{(r.scheduledHours - config.periodHoursCap).toFixed(1)}h over)</span>}
                    {r.hoursCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.hoursCapPct * 100)}%)</span>}
                  </div>
                </td>
                <td className="num-cell">{r.outsideHours.toFixed(1)}h</td>
                <td>
                  <ProgressBar pct={r.outsideCapPct} status={r.outsideCapPct > 1 ? "over" : r.outsideCapPct >= config.nearLimitThreshold ? "near" : "ok"} />
                  <div className="compliance-bar-label">
                    {r.outsideHours.toFixed(1)}/{config.periodOutsideHoursCap}h
                    {r.outsideCapPct > 1 && <span style={{ color: "var(--impacted-high)" }}> (+{(r.outsideHours - config.periodOutsideHoursCap).toFixed(1)}h over)</span>}
                    {r.outsideCapPct <= 1 && <span style={{ color: "var(--text-muted)" }}> ({Math.round(r.outsideCapPct * 100)}%)</span>}
                  </div>
                </td>
                <td style={{ textAlign: "center" }}>
                  <StatusBadge status={r.complianceStatus} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add Compliance CSS to `src/styles.css`**

```css
/* Compliance tab */
.compliance-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.compliance-violation-banner {
  background: var(--impacted-high-bg);
  border: 1px solid var(--impacted-high);
  border-radius: 6px;
  padding: 8px 16px;
  margin: 8px 16px 0;
  font-size: 12px;
  color: var(--text-primary);
  flex-shrink: 0;
}

.compliance-bar-wrap { margin-bottom: 2px; }

.compliance-bar-track {
  background: var(--bg-card);
  border-radius: 3px;
  height: 8px;
  overflow: hidden;
  width: 100%;
  min-width: 80px;
}

.compliance-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.compliance-bar-label {
  font-size: 9px;
  color: var(--text-muted);
  margin-top: 2px;
}

.compliance-row--over td { background: color-mix(in srgb, var(--impacted-high) 5%, transparent); }

.compliance-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  border-radius: 4px;
  padding: 2px 6px;
  white-space: nowrap;
}

.compliance-badge--ok   { background: var(--pd-green-bg); color: var(--pd-green); }
.compliance-badge--near { background: var(--ooh-orange-bg); color: var(--ooh-orange); }
.compliance-badge--over { background: var(--impacted-high-bg); color: var(--impacted-high); }
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/components/ComplianceTab.tsx mcp-apps/oncall-compensation/src/styles.css
git commit -m "feat(compensation): add ComplianceTab component"
```

---

## Task 11: Create FairnessTab component

**Files:**
- Create: `mcp-apps/oncall-compensation/src/components/FairnessTab.tsx`

- [ ] **Step 1: Create `FairnessTab.tsx`**

```tsx
// src/components/FairnessTab.tsx

import type { FairnessData } from "../fairness";
import { InfoIcon } from "./InfoIcon";

interface Props {
  data: FairnessData;
  outlierMultiplier: number;
}

export function FairnessTab({ data, outlierMultiplier }: Props) {
  const maxHours = Math.max(...data.outliers.map((o) => o.scheduledHours), ...data.teams.flatMap(() => []), data.globalAvgHours * outlierMultiplier * 1.2, 1);

  // Build bar chart entries: outliers (red) + top non-outliers (green), max 20
  const allRecordsForChart = [
    ...data.outliers,
    // remaining users not in outliers: derive from teams
  ];

  const equityColor = (score: number) =>
    score >= 80 ? "var(--pd-green)" : score >= 60 ? "var(--ooh-orange)" : "var(--impacted-high)";

  return (
    <div className="fairness-tab">
      {/* Summary cards */}
      <div className="summary-cards" style={{ padding: "8px 16px" }}>
        <div className="summary-card">
          <div className="card-value">{data.globalAvgHours}h</div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Avg Hours / Person
            <InfoIcon text="Mean scheduled oncall hours across all users in the selected period." />
          </div>
        </div>
        <div className="summary-card">
          <div className="card-value" style={{ color: data.globalStdDev > data.globalAvgHours * 0.5 ? "var(--ooh-orange)" : "var(--text-primary)" }}>
            {data.globalStdDev}h
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Std Deviation
            <InfoIcon text="Standard deviation of scheduled hours across all users. High deviation = uneven distribution." />
          </div>
        </div>
        <div className="summary-card" style={{ borderColor: data.outliers.length > 0 ? "var(--impacted-high-bg)" : undefined }}>
          <div className="card-value" style={{ color: data.outliers.length > 0 ? "var(--impacted-high)" : "var(--text-muted)" }}>
            {data.outliers.length}
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Outliers
            <InfoIcon text={`Users carrying ≥ ${outlierMultiplier}× the global average oncall hours. Configurable in Settings.`} />
          </div>
          <div className="card-sub">&gt;{outlierMultiplier}× avg load</div>
        </div>
        <div className="summary-card">
          <div className="card-value" style={{ color: equityColor(data.globalEquityScore) }}>
            {data.globalEquityScore} / 100
          </div>
          <div className="card-label" style={{ display: "flex", alignItems: "center", gap: 4 }}>
            Equity Score
            <InfoIcon text="Equity Score = 100 − (std deviation ÷ mean × 100), capped 0–100. Score of 100 = perfectly equal distribution. Lower = higher variance in oncall burden." />
          </div>
        </div>
      </div>

      <div className="fairness-body">
        {/* Outlier cards */}
        {data.outliers.length > 0 && (
          <div className="fairness-outliers">
            <h4 className="fairness-section-title">
              ⚠ Outliers — carrying {outlierMultiplier}×+ average load
              <InfoIcon text={`These users have scheduled hours ≥ ${outlierMultiplier}× the global average of ${data.globalAvgHours}h.`} />
            </h4>
            <div className="outlier-cards">
              {data.outliers.map((o) => (
                <div key={o.userId} className="outlier-card">
                  <div className="outlier-card-header">
                    <span className="outlier-name">{o.userName}</span>
                    <span className="outlier-badge">{o.multiplierVsAvg}× avg</span>
                  </div>
                  <div className="outlier-detail">
                    {o.scheduledHours.toFixed(1)}h total
                    {o.outsideHours > 0 && ` · ${o.outsideHours.toFixed(1)}h outside-hours`}
                    {` · ${o.totalInterruptions} interruptions`}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Team equity table */}
        <div className="fairness-team-table">
          <h4 className="fairness-section-title">
            Team equity breakdown
            <InfoIcon text="Equity Score per team = 100 − (team std deviation ÷ team mean × 100). Lower score = more uneven burden within that team." />
          </h4>
          <table className="comp-table">
            <thead>
              <tr>
                <th>Team</th>
                <th style={{ textAlign: "right" }}>Members</th>
                <th style={{ textAlign: "right" }}>Avg Hours</th>
                <th style={{ textAlign: "right" }}>
                  Std Dev
                  <InfoIcon text="Standard deviation of scheduled hours within this team." />
                </th>
                <th style={{ textAlign: "right" }}>
                  Outliers
                  <InfoIcon text={`Members carrying ≥ ${outlierMultiplier}× their team average.`} />
                </th>
                <th style={{ textAlign: "center" }}>Equity</th>
              </tr>
            </thead>
            <tbody>
              {data.teams.map((t) => (
                <tr key={t.teamId}>
                  <td>{t.teamName}</td>
                  <td className="num-cell">{t.memberCount}</td>
                  <td className="num-cell">{t.avgHours}h</td>
                  <td className="num-cell" style={{ color: t.stdDev > t.avgHours * 0.5 ? "var(--ooh-orange)" : undefined }}>{t.stdDev}h</td>
                  <td className="num-cell" style={{ color: t.outlierCount > 0 ? "var(--impacted-high)" : undefined }}>{t.outlierCount}</td>
                  <td style={{ textAlign: "center" }}>
                    <span className="equity-badge" style={{ color: equityColor(t.equityScore), background: "transparent", border: `1px solid ${equityColor(t.equityScore)}` }}>
                      {t.equityScore} / 100
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add Fairness CSS to `src/styles.css`**

```css
/* Fairness tab */
.fairness-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.fairness-body {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.fairness-section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.fairness-outliers { }

.outlier-cards {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.outlier-card {
  background: var(--impacted-high-bg);
  border: 1px solid var(--impacted-high);
  border-radius: 5px;
  padding: 8px 12px;
}

.outlier-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3px;
}

.outlier-name {
  font-weight: 600;
  font-size: 12px;
  color: var(--impacted-high);
}

.outlier-badge {
  font-size: 10px;
  background: var(--impacted-high-bg);
  color: var(--impacted-high);
  border: 1px solid var(--impacted-high);
  border-radius: 3px;
  padding: 1px 6px;
}

.outlier-detail {
  font-size: 10px;
  color: var(--text-secondary);
}

.fairness-team-table { }

.equity-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  border-radius: 4px;
  padding: 2px 6px;
}
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/components/FairnessTab.tsx mcp-apps/oncall-compensation/src/styles.css
git commit -m "feat(compensation): add FairnessTab component"
```

---

## Task 12: Wire everything together in `mcp-app.tsx`

**Files:**
- Modify: `mcp-apps/oncall-compensation/src/mcp-app.tsx`

- [ ] **Step 1: Replace `mcp-app.tsx` with the wired-up version**

Replace the entire file with:

```tsx
import type { App as McpApp } from "@modelcontextprotocol/ext-apps";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchCompensationData } from "./api";
import type { CompensationData, UserCompensationRecord } from "./api";
import { computeOutsideHoursMetrics } from "./businessHours";
import { loadSettings, saveSettings } from "./config";
import type { AllSettings } from "./config";
import { computeEstimatedPay } from "./compensation";
import { deriveComplianceRecords } from "./compliance";
import { computeFairnessData } from "./fairness";
import { TabBar } from "./components/TabBar";
import type { TabId } from "./components/TabBar";
import { CompensationTab } from "./components/CompensationTab";
import { ComplianceTab } from "./components/ComplianceTab";
import { FairnessTab } from "./components/FairnessTab";
import { SettingsTab } from "./components/SettingsTab";
import { UserDetailModal } from "./components/UserDetailModal";
import type { SortKey } from "./components/CompensationTable";

function getDefaultSince(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0]!;
}

function getToday(): string {
  return new Date().toISOString().split("T")[0]!;
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Oncall Compensation & Compliance", version: "2.0.0" },
    capabilities: {},
  });

  const [data, setData] = useState<CompensationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [activeTab, setActiveTab] = useState<TabId>("compensation");
  const [settings, setSettings] = useState<AllSettings>(loadSettings);

  // Compensation tab state
  const [search, setSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("");
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("scheduledHours");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [visibleCols, setVisibleCols] = useState<Set<SortKey>>(
    () =>
      new Set<SortKey>([
        "scheduledHours",
        "incidentCount",
        "interruptionRate",
        "offHourInterruptions",
        "sleepHourInterruptions",
        "outsideHours",
        "weekendHours",
        "uniquePeriodsOutside",
        "estimatedPay",
      ]),
  );
  const [colPickerOpen, setColPickerOpen] = useState(false);
  const [showSummary, setShowSummary] = useState(true);
  const [displayMode, setDisplayMode] = useState<"inline" | "fullscreen" | "pip">("inline");

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if (ctx.displayMode) setDisplayMode(ctx.displayMode);
    };
  }, [app]);

  useEffect(() => {
    if (!app) return;
    let cancelled = false;
    async function load(appInstance: McpApp) {
      setLoading(true);
      setError(null);
      setSelectedUserId(null);
      try {
        const result = await fetchCompensationData(appInstance, `${since}T00:00:00Z`, `${until}T23:59:59Z`);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load(app);
    return () => { cancelled = true; };
  }, [app, since, until]);

  // Chain of derived memos
  const enrichedRecords = useMemo((): UserCompensationRecord[] => {
    if (!data) return [];
    return data.records.map((r) => {
      if (r.oncallShifts.length === 0) return { ...r, estimatedPay: 0 };
      const m = computeOutsideHoursMetrics(r.oncallShifts, settings.businessHours);
      return {
        ...r,
        outsideHours: m.totalOutsideHours,
        weekendHours: m.totalWeekendHours,
        holidayHours: m.totalHolidayHours,
        maxConsecutiveOutsideHours: m.maxConsecutiveOutsideHours,
        uniquePeriodsOutside: m.uniquePeriodsOutside,
        estimatedPay: 0,
      };
    });
  }, [data, settings.businessHours]);

  const compensatedRecords = useMemo(() =>
    enrichedRecords.map((r) => ({
      ...r,
      estimatedPay: computeEstimatedPay(r, settings.pay),
    })),
    [enrichedRecords, settings.pay],
  );

  const complianceRecords = useMemo(() =>
    deriveComplianceRecords(compensatedRecords, settings.compliance),
    [compensatedRecords, settings.compliance],
  );

  const fairnessData = useMemo(() =>
    computeFairnessData(compensatedRecords, settings.fairness),
    [compensatedRecords, settings.fairness],
  );

  const handleSort = (key: SortKey) => {
    if (key === sortKey) setSortDir((d) => (d === "desc" ? "asc" : "desc"));
    else { setSortKey(key); setSortDir("desc"); }
  };

  const filteredRecords = useMemo(() => {
    const q = search.toLowerCase().trim();
    let list = compensatedRecords;
    if (q) list = list.filter((r) => r.userName.toLowerCase().includes(q) || (r.teamName?.toLowerCase().includes(q) ?? false));
    if (teamFilter) list = list.filter((r) => r.teamIds.includes(teamFilter));
    return [...list].sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      if (sortKey === "userName") return a.userName.localeCompare(b.userName) * dir;
      return ((a[sortKey] as number) - (b[sortKey] as number)) * dir;
    });
  }, [compensatedRecords, search, teamFilter, sortKey, sortDir]);

  const selectedRecord = selectedUserId
    ? compensatedRecords.find((r) => r.userId === selectedUserId) ?? null
    : null;

  const displayError = connectionError?.message ?? error;

  const handleSaveSettings = (s: AllSettings) => {
    setSettings(s);
    saveSettings(s);
  };

  const doRefresh = () => { const s = since; setSince(""); setTimeout(() => setSince(s), 0); };

  return (
    <div className="app" data-theme="dark">
      <header className="header">
        <div className="header-left">
          <PagerDutyIcon />
          <div>
            <div className="header-title">Oncall Compensation & Compliance</div>
            <div className="header-subtitle">
              {data ? `${data.records.length} user${data.records.length !== 1 ? "s" : ""}` : loading ? "Loading…" : "No data"}
            </div>
          </div>
        </div>
        <div className="header-dates">
          <span className="header-date-label">From</span>
          <input type="date" className="header-date-input" value={since} max={until} onChange={(e) => setSince(e.target.value)} disabled={loading} />
          <span className="header-date-label">To</span>
          <input type="date" className="header-date-input" value={until} min={since} max={getToday()} onChange={(e) => setUntil(e.target.value)} disabled={loading} />
          <button className="btn-refresh-header" disabled={loading} onClick={doRefresh}>
            <span className="pd-dot" />{loading ? "Loading…" : "Refresh"}
          </button>
        </div>
        <button
          className="btn-expand"
          onClick={async () => {
            if (!app) return;
            await app.requestDisplayMode({ mode: displayMode === "fullscreen" ? "inline" : "fullscreen" });
          }}
          title={displayMode === "fullscreen" ? "Exit fullscreen" : "Expand to fullscreen"}
        >
          {displayMode === "fullscreen" ? "⤡" : "⤢"}
        </button>
      </header>

      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Team/search controls — shown only on Compensation tab */}
      {activeTab === "compensation" && (
        <div className="controls">
          {(data?.teams.length ?? 0) > 0 && (
            <select value={teamFilter} onChange={(e) => { setTeamFilter(e.target.value); setSelectedUserId(null); }} disabled={loading}>
              <option value="">All teams</option>
              {(data?.teams ?? []).map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          )}
          <div className="search-wrap">
            <SearchIcon />
            <input type="text" placeholder="Search users or teams…" value={search} onChange={(e) => setSearch(e.target.value)} disabled={loading} />
          </div>
        </div>
      )}

      <div className="main-content">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner" />
            <span>Loading data…</span>
          </div>
        )}
        {!loading && displayError && <div className="error-banner">⚠ {displayError}</div>}

        {!loading && (
          <>
            {activeTab === "compensation" && (
              <CompensationTab
                records={filteredRecords}
                selectedId={selectedUserId}
                onSelect={(id) => setSelectedUserId((cur) => (cur === id ? null : id))}
                sortKey={sortKey}
                sortDir={sortDir}
                onSort={handleSort}
                visibleCols={visibleCols}
                onVisibleColsChange={setVisibleCols}
                colPickerOpen={colPickerOpen}
                onColPickerToggle={() => setColPickerOpen((o) => !o)}
                onColPickerClose={() => setColPickerOpen(false)}
                showSummary={showSummary}
                onToggleSummary={() => setShowSummary((s) => !s)}
              />
            )}
            {activeTab === "compliance" && (
              <ComplianceTab records={complianceRecords} config={settings.compliance} />
            )}
            {activeTab === "fairness" && (
              <FairnessTab data={fairnessData} outlierMultiplier={settings.fairness.outlierMultiplier} />
            )}
            {activeTab === "settings" && (
              <SettingsTab settings={settings} onSave={handleSaveSettings} />
            )}
          </>
        )}
      </div>

      {selectedRecord && (
        <UserDetailModal record={selectedRecord} onClose={() => setSelectedUserId(null)} />
      )}
    </div>
  );
}

function SearchIcon() {
  return (
    <svg className="search-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="6.5" cy="6.5" r="4" />
      <path d="M11 11l3 3" strokeLinecap="round" />
    </svg>
  );
}

function PagerDutyIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="16" fill="#06AC38" />
      <path d="M35 25h18c10 0 18 7 18 17s-8 17-18 17H47v16H35V25zm12 24h5c4.5 0 7-2.5 7-7s-2.5-7-7-7H47v14z" fill="white" />
    </svg>
  );
}

const container = document.getElementById("root");
if (container) {
  createRoot(container).render(<StrictMode><App /></StrictMode>);
}
```

- [ ] **Step 2: Build and verify no TypeScript errors**

```bash
cd mcp-apps/oncall-compensation && source ~/.nvm/nvm.sh && nvm use && npm run build 2>&1 | tail -30
```

Expected: build succeeds with no TypeScript errors. If errors appear, fix them before committing.

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-compensation/src/mcp-app.tsx
git commit -m "feat(compensation): wire tabs, settings, and derived data into mcp-app"
```

---

## Task 13: Build, copy, and smoke-test

**Files:**
- Modify: `pagerduty_mcp/oncall_compensation_view.html`

- [ ] **Step 1: Run a full build**

```bash
cd mcp-apps/oncall-compensation && source ~/.nvm/nvm.sh && nvm use && npm run build 2>&1 | tail -20
```

Expected: `dist/mcp-app.html` generated with no errors.

- [ ] **Step 2: Copy built file**

```bash
cp mcp-apps/oncall-compensation/dist/mcp-app.html pagerduty_mcp/oncall_compensation_view.html && echo "copied"
```

- [ ] **Step 3: Verify the HTML file was updated**

```bash
ls -lh pagerduty_mcp/oncall_compensation_view.html
```

Expected: file timestamp matches the current build.

- [ ] **Step 4: Commit**

```bash
git add pagerduty_mcp/oncall_compensation_view.html
git commit -m "feat(compensation): build and deploy unified compensation & compliance app"
```
