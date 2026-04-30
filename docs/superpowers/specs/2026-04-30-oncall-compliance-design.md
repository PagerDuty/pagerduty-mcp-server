# Oncall Compensation & Compliance — Design Spec

**Date:** 2026-04-30  
**Status:** Approved  
**App:** `mcp-apps/oncall-compensation` (ext-apps SDK, `mcp-apps/` folder)

---

## Goal

Evolve the existing `oncall-compensation` MCP app into a unified **Oncall Compensation & Compliance** tool with four tabs: Compensation, Compliance, Fairness, and Settings. All tabs share a single data fetch (real PagerDuty data). Configuration persists in `localStorage`.

---

## Approach

Extend the existing app in-place — no new app scaffolding needed. The existing `fetchCompensationData()` and `computeOutsideHoursMetrics()` logic remain unchanged. New tabs and settings are layered on top.

---

## Architecture

### Data flow

```
useEffect (app, since, until)
  └─ fetchCompensationData() — unchanged, fetches from PD Analytics + list_oncalls
       └─ returns CompensationData { records, teams, since, until }

useMemo (data, bhConfig)
  └─ enrichedRecords — recomputes outside-hours metrics per user

useMemo (enrichedRecords, payConfig)
  └─ compensatedRecords — adds estimatedPay per user

useMemo (compensatedRecords, complianceConfig)
  └─ complianceRecords — adds status (ok | near | over) per user

useMemo (compensatedRecords, fairnessConfig)
  └─ fairnessData — computes team/global equity scores, outliers
```

All derived data is computed in the browser from the same base fetch. No new API calls for compliance or fairness views.

### File structure changes

```
mcp-apps/oncall-compensation/src/
  mcp-app.tsx                  ← add tab state, settings state, top-level layout
  api.ts                       ← unchanged
  businessHours.ts             ← unchanged
  styles.css                   ← extend for tabs + new components
  config.ts                    ← NEW: PayConfig, ComplianceConfig, FairnessConfig types + localStorage persistence
  compensation.ts              ← NEW: estimatedPay computation logic
  compliance.ts                ← NEW: compliance status derivation logic
  fairness.ts                  ← NEW: equity score, outlier detection logic
  components/
    TabBar.tsx                 ← NEW: tab navigation
    CompensationTab.tsx        ← NEW: wraps existing table/summary, adds Est. Pay column
    ComplianceTab.tsx          ← NEW: compliance table with progress bars + status badges
    FairnessTab.tsx            ← NEW: distribution chart + outlier cards + team breakdown
    SettingsTab.tsx            ← NEW: all config panels in two-column layout
    InfoIcon.tsx               ← NEW: reusable ℹ tooltip component
    SummaryCards.tsx           ← existing, extend to add Est. Pay card
    CompensationTable.tsx      ← existing, extend to add estimatedPay column
    UserDetailModal.tsx        ← existing, unchanged
    BusinessHoursConfig.tsx    ← existing, moved into SettingsTab
    ColumnPicker.tsx           ← existing, unchanged
```

---

## Tab Designs

### Compensation tab

Keeps everything from the current app plus:
- **Est. Compensation** summary card (sum of all users' estimated pay)
- **Est. Pay** column in the table, sortable
- Business Hours config button **removed** from header — moved to Settings tab

### Compliance tab

- **Violation banner** at top if any users exceed caps
- **Summary cards**: compliant count, violation count, period total cap, outside-hours cap
- **Per-user table** with columns: User, Team, Sched Hours, vs. Period Cap (progress bar), Outside Hrs, vs. Outside Cap (progress bar), Status badge
- **Three status levels**:
  - `✓ OK` — below near-limit threshold
  - `⚡ NEAR` — within `nearThreshold`% of cap (default 90%)
  - `⚠ OVER CAP` — exceeded period total cap or outside-hours cap

### Fairness tab

- **Summary cards**: avg hours/person, std deviation, outlier count, equity score
- **Horizontal bar chart** — all users sorted high→low, outliers in red, average line marker
- **Outlier cards** — users carrying ≥ `outlierMultiplier`× team average, showing hours + outside-hours + interruptions
- **Team equity table** — per team: member count, avg hours, std dev, outlier count, equity score badge
- **Equity Score formula**: `100 − (stdDev / mean × 100)`, capped 0–100. Displayed with ℹ tooltip.
- **Outlier threshold**: configurable (default 2×), displayed with ℹ tooltip.
- **ℹ icons** on all computed metrics explaining the formula

### Settings tab

Two-column layout. All settings saved to `localStorage` on "Save Settings". Resets to defaults on "Reset to defaults".

**Left column:**

1. **Pay Rates**
   - L1 (Primary) base rate $/hr
   - L2+ (Secondary) base rate $/hr
   - Multipliers: Off-Hours ×, Weekend ×, Holiday ×
   - ℹ tooltip: `Est. pay = (L1 hrs × L1 rate × multiplier) + (L2+ hrs × L2+ rate × multiplier)`

2. **Compliance Caps**
   - Period total cap (hrs)
   - Period outside-hours cap (hrs)
   - Near-limit warning threshold % (slider, default 90%)
   - ℹ tooltip explaining each field

**Right column:**

3. **Business Hours** (migrated from existing `BusinessHoursConfig` component)
   - Start hour / End hour
   - Work days toggle (S M T W T F S)
   - Timezone dropdown (IANA)

4. **Fairness Thresholds**
   - Outlier threshold slider (1.5× – 5×, default 2×)
   - ℹ tooltip explaining outlier calculation

---

## Configuration Types

```typescript
// config.ts

export interface PayConfig {
  l1RatePerHour: number;       // default: 20
  l2PlusRatePerHour: number;   // default: 15
  offHoursMultiplier: number;  // default: 1.5
  weekendMultiplier: number;   // default: 2.0
  holidayMultiplier: number;   // default: 2.5
}

export interface ComplianceConfig {
  periodHoursCap: number;         // default: 160 (applies to whatever date range is selected)
  periodOutsideHoursCap: number;  // default: 60
  nearLimitThreshold: number;      // default: 0.9 (90%)
}

export interface FairnessConfig {
  outlierMultiplier: number;  // default: 2.0
}

export type ComplianceStatus = "ok" | "near" | "over";
```

---

## Compensation Calculation

`oncallShifts` from PagerDuty do not carry level information, so outside-hours cannot be split by L1 vs L2+. The model applies level rates to the full scheduled hour blocks, then adds outside-hours premiums on top of the L1 rate (primary oncall carries the outside-hours burden):

```
// Per user (all values from enrichedRecords):
insideHours  = scheduledHours − outsideHours − weekendHours − holidayHours
               (business-hours portion of total scheduled time)

estimatedPay =
  (insideHours          × l1Rate)
  + (outsideHours       × l1Rate × offHoursMultiplier)
  + (weekendHours       × l1Rate × weekendMultiplier)
  + (holidayHours       × l1Rate × holidayMultiplier)
  + (scheduledHoursL2Plus × l2PlusRate)
```

`insideHours`, `outsideHours`, `weekendHours`, `holidayHours` all come from the existing `enrichedRecords` memo (computed by `businessHours.ts` — no new API data needed). `scheduledHoursL2Plus` comes directly from PagerDuty Analytics.

The ℹ tooltip in Settings explains this model clearly so users understand it's an estimate.

---

## Equity Score

```
mean = sum(scheduledHours) / userCount
stdDev = sqrt(sum((hours - mean)²) / userCount)
equityScore = max(0, min(100, Math.round(100 - (stdDev / mean * 100))))
```

Computed per-team and globally. Score of 100 = perfectly equal distribution; lower = higher variance.

---

## Settings Persistence

Settings are stored in `localStorage` under a single key `oncall-compliance-settings` as a JSON blob containing `PayConfig`, `ComplianceConfig`, `FairnessConfig`, and `BusinessHoursConfig`. On mount, the app reads from `localStorage` and falls back to defaults if absent or malformed.

Holidays in `BusinessHoursConfig` are serialized as a sorted array of `"YYYY-MM-DD"` strings and deserialized back into a `Set<string>`. `WorkDays` similarly serialized as an array of day numbers.

---

## Header Changes

- Remove the "⚙ Business Hours" button from the header
- Add tab bar below the header (Compensation · Compliance · Fairness · Settings)
- Header title changes to "Oncall Compensation & Compliance"
- Fullscreen and date range controls remain in the header

---

## Error Handling

- If `fetchCompensationData()` fails, show existing error banner on all tabs
- If a user has no `oncallShifts`, their outside-hours and estimated pay default to 0 (existing behavior, unchanged)
- If settings in `localStorage` are malformed (e.g. `NaN` rate), silently fall back to defaults

---

## Out of Scope

- Per-user pay rate overrides (Phase 2)
- Agentic / conversational UX (Phase 2)
- Region-aware automatic holiday calendars (Phase 2 — holidays manually entered in Settings for now)
- Export to CSV/PDF (Phase 2)
