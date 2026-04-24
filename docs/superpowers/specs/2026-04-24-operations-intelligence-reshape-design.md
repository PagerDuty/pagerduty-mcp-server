# Operations Intelligence Reshape — Design Spec

**Date:** 2026-04-24  
**Status:** Approved  
**Branch:** feature/new-mcp-apps

---

## Summary

Reshape the Operations Intelligence MCP app from a tab-based layout into a **home-menu + multi-page navigation** design inspired by PagerDuty Insights. Add **Oncall Compensation** as a new first-class page. Apply a refined data-dense visual design: `Syne` + `DM Mono` + `Outfit` typography, color-coded section cards, Bloomberg-style KPI bar.

---

## Problem / Motivation

The current app opens directly into three flat tabs (Operational, Team Health, Trends). As more sections have been added (and Oncall Compensation should be added), this flat tab model becomes overloaded and doesn't communicate what's available at a glance. A home-menu pattern — as used by PagerDuty's own Insights page — lets users orient themselves and navigate intentionally.

---

## Architecture

### Navigation Model

- **Home screen** (`page = "home"`) — 3-column card grid, one card per section
- **Section pages** (`page = "service" | "team" | "responder" | "teamHealth" | "trends" | "compensation"`) — full-page content
- Navigation via **persistent tab bar** (matches PagerDuty Insights UX exactly):
  - Tabs: `Home · Service Metrics · Team Metrics · Responder · Team Health · Trends · Compensation`
  - Active tab highlighted with PD green underline + small dot indicator
- Date range + team filter controls live in the **app header**, shared across all pages
- No modals or overlays for navigation — pure tab switching

### State

```ts
type Page = "home" | "service" | "team" | "responder" | "teamHealth" | "trends" | "compensation";
```

`useState<Page>("home")` in the root `App` component. Clicking a menu card OR a tab sets the active page.

---

## Visual Design System

### Typography
| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Headings | Syne | 700–800 | App title, home intro h2, card titles |
| Body | Outfit | 300–600 | Descriptions, labels, controls |
| Data / Mono | DM Mono | 400–500 | All numbers, KPI values, table data, pills |

Google Fonts import:
```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
```

### Color Tokens (CSS variables)
```css
--bg: #F7F7F5
--surface: #FFFFFF
--surface-2: #F2F2F0
--border: #E8E8E4
--border-2: #D4D4CE
--text-1: #111110       /* primary */
--text-2: #5A5A54       /* secondary */
--text-3: #9A9A92       /* tertiary / labels */
--green: #06AC38        /* PD green — primary accent */
--green-dim: rgba(6,172,56,.10)
--amber: #D97706        /* warnings */
--amber-dim: rgba(217,119,6,.10)
--red: #DC2626
--red-dim: rgba(220,38,38,.10)
--blue: #2563EB
--blue-dim: rgba(37,99,235,.10)
--violet: #7C3AED
--violet-dim: rgba(124,58,237,.10)
--teal: #0891B2
--teal-dim: rgba(8,145,178,.10)
```

Dark mode: keep existing `data-theme="dark"` mechanism, map tokens accordingly.

### Card Color Coding (home menu)
Each card gets a CSS custom property `--card-accent` + `--card-icon-bg`:

| Section | Accent | Icon BG |
|---------|--------|---------|
| Service Metrics | `--green` | `--green-dim` |
| Team Metrics | `--blue` | `--blue-dim` |
| Responder | `--violet` | `--violet-dim` |
| Team Health | `--teal` | `--teal-dim` |
| Trends | `--amber` | `--amber-dim` |
| Oncall Compensation | `--red` | `--red-dim` |

Left-border accent reveal on hover (scaleY animation from center).

### KPI Bar
- Borderless row of cells, each separated by a `1px` right border
- Colored underline (`2px`) appears on hover using `::after` pseudo-element
- All values in `DM Mono`
- Warn values colored `--amber`

### Animations
- Menu cards: `fadeSlideUp` staggered entry (40ms delay increments, 6 cards)
- KPI cells: same stagger on page enter
- Card hover: `translateY(-2px)` + shadow + left-border scaleY reveal

---

## Pages

### Home
- Intro text: "What would you like to explore?" + subtitle
- 3-column card grid, 6 cards
- Each card: icon (36×36 rounded bg), title (Syne 700), description (Outfit 12px), pills (DM Mono tags)
- Clicking a card navigates to that page (sets `page` state)

### Service Metrics (existing `ServiceBreakdown` + `SummaryCards`)
- KPI bar: Total Incidents, MTTA, MTTR, Avg Uptime, Escalation Rate
- Table: service name, team, incident bar chart, MTTA, MTTR, Uptime badge
- Reuses existing `ServiceBreakdown` and `SummaryCards` components, restyled

### Team Metrics (existing `TeamBreakdown`)
- KPI bar derived from `teamMetrics` aggregate
- Table: team name, incidents, MTTA, MTTR, escalations, interruptions
- Reuses existing `TeamBreakdown` component, restyled

### Responder Metrics (existing `ResponderLoad`)
- KPI bar: total responders, avg on-call hours, total interruptions, high-risk count
- Table: name, team, on-call hours, incidents, sleep interruptions, risk badge
- Reuses existing `ResponderLoad` component, restyled

### Team Health (existing `TeamHealth`)
- Fatigue KPI summary cards (high/medium/low risk counts)
- Responder table with risk badges and row tinting
- Reuses existing `TeamHealth` component, restyled

### Trends (existing `TrendsTab`)
- Date-range scoped weekly charts: incident volume, MTTA, MTTR, interruptions
- No KPI bar — charts are the primary content
- Reuses existing `TrendsTab` component, restyled

### Oncall Compensation (**NEW page**)
- New self-contained page within Operations Intelligence — does NOT import from `oncall-compensation/` package (cross-package imports don't work without build config changes)
- **Strategy**: add a `fetchCompensationPageData(app, since, until, teamId)` function directly in `operations-intelligence/src/api.ts` that calls:
  - `list_oncalls` (with `since`/`until` time_since/time_until params) to get per-user shift data
  - `get_responder_load_metrics` (already called by `fetchOpsData`) — reuse the `responderMetrics` already in `OpsData` rather than re-fetching
- **Date range** comes from the shared app-level `since`/`until` state (no separate date inputs on this page)
- `CompensationPage.tsx` is a new self-contained component that renders the data; no dependency on `oncall-compensation/src/`
- Show: per-user on-call hours, scheduled shifts count, sleep interruptions, engaged minutes, risk level
- KPI bar: total users, total on-call hours (sum), avg on-call hours/user, high-risk responder count
- **Simplification**: since `responderMetrics` already contains `onCallHours`, `sleepInterruptions`, `engagedMinutes`, `riskLevel` — the compensation page can reuse `OpsData.responderMetrics` directly with no additional API calls

---

## Files to Change

### Primary
| File | Change |
|------|--------|
| `mcp-apps/operations-intelligence/src/mcp-app.tsx` | Replace 3-tab layout with Page state + home menu + tab nav |
| `mcp-apps/operations-intelligence/src/styles.css` | Full restyle: new tokens, typography, card styles, KPI bar, tab nav |
| `mcp-apps/operations-intelligence/src/api.ts` | No changes needed — `responderMetrics` in `OpsData` already has all compensation data |

### New Components
| File | Purpose |
|------|---------|
| `mcp-apps/operations-intelligence/src/components/HomePage.tsx` | 3×2 card grid menu |
| `mcp-apps/operations-intelligence/src/components/CompensationPage.tsx` | Compensation page (wraps oncall-compensation logic) |

### Existing Components — Restyled (CSS only, no logic changes)
- `SummaryCards.tsx` — update class names to use new KPI bar styles
- `ServiceBreakdown.tsx`, `TeamBreakdown.tsx`, `ResponderLoad.tsx`, `TeamHealth.tsx`, `TrendsTab.tsx`, `PercentileSection.tsx` — only CSS class updates if needed; logic unchanged

---

## Data Loading Strategy

All data still loaded in a single `fetchOpsData()` call on mount (unchanged). The Compensation page reuses `OpsData.responderMetrics` — no additional API calls needed. This means:

- Zero extra loading time when navigating to Compensation
- `CompensationPage` receives `responderMetrics: ResponderMetric[]` as a prop
- Displays: name, team, on-call hours, total incidents, sleep interruptions, engaged minutes, risk badge

---

## Verification

1. **Build**: `cd mcp-apps/operations-intelligence && npm run build` — no TypeScript errors
2. **Mock mode**: `VITE_MOCK=true npm run dev` — all 6 pages render with mock data
3. **Navigation**: clicking each home card navigates to the correct page; tab bar reflects active page
4. **Compensation page**: loads data independently when navigated to; respects shared date/team filters
5. **Existing pages**: Operational, Team Health, Trends data unchanged — only styling updated
6. **Dark mode**: `?theme=dark` URL param applies correctly across all pages
7. **Build output** registered in `pagerduty_mcp/server.py` and `mcp-apps/build-all.sh` (no changes needed — same app)
