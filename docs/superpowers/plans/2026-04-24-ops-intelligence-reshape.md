# Operations Intelligence Reshape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reshape the Operations Intelligence MCP app into a home-menu + multi-page navigation design with a new Oncall Compensation page and a refined Syne/DM Mono/Outfit visual design system.

**Architecture:** Replace the current 3-tab layout with a `Page` state machine (`"home" | "service" | "team" | "responder" | "teamHealth" | "trends" | "compensation"`). A persistent tab bar (matching PagerDuty Insights) sits below the header; clicking a tab or a home-screen card sets `page`. All data is still fetched in one `fetchOpsData()` call — the Compensation page reuses `OpsData.responderMetrics` with zero extra API calls.

**Tech Stack:** React 18, TypeScript, Vite, `@modelcontextprotocol/ext-apps`, Google Fonts (Syne + DM Mono + Outfit), existing SVG chart components.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| **Modify** | `src/styles.css` | Full restyle — design tokens, typography, tab nav, home cards, KPI bar |
| **Modify** | `src/mcp-app.tsx` | Replace tab state with `Page` state, add tab nav + home render |
| **Create** | `src/components/HomePage.tsx` | 3×2 color-coded card grid menu |
| **Create** | `src/components/CompensationPage.tsx` | Compensation page using `responderMetrics` |
| **Modify** | `src/components/SummaryCards.tsx` | Update CSS class names to new design system |
| **Modify** | `src/components/ServiceBreakdown.tsx` | Update CSS class names |
| **Modify** | `src/components/TeamBreakdown.tsx` | Update CSS class names |
| **Modify** | `src/components/ResponderLoad.tsx` | Update CSS class names |
| **Modify** | `src/components/TeamHealth.tsx` | Update CSS class names |
| **Modify** | `src/components/TrendsTab.tsx` | Update CSS variable references |
| **Modify** | `src/components/PercentileSection.tsx` | Update CSS class names |
| **No change** | `src/api.ts` | Unchanged — `OpsData` already has all needed data |
| **No change** | `src/mock.ts` | Unchanged |
| **No change** | `src/utils.ts` | Unchanged |

All paths are relative to `mcp-apps/operations-intelligence/`.

---

## Task 1: Replace styles.css with new design system

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/styles.css`

- [ ] **Step 1: Replace the entire styles.css**

```css
/* Operations Intelligence — Design System v3 */

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Tokens ── */
:root {
  --bg:          #F7F7F5;
  --surface:     #FFFFFF;
  --surface-2:   #F2F2F0;
  --border:      #E8E8E4;
  --border-2:    #D4D4CE;
  --text-1:      #111110;
  --text-2:      #5A5A54;
  --text-3:      #9A9A92;
  --green:       #06AC38;
  --green-dim:   rgba(6,172,56,.10);
  --amber:       #D97706;
  --amber-dim:   rgba(217,119,6,.10);
  --red:         #DC2626;
  --red-dim:     rgba(220,38,38,.10);
  --blue:        #2563EB;
  --blue-dim:    rgba(37,99,235,.10);
  --violet:      #7C3AED;
  --violet-dim:  rgba(124,58,237,.10);
  --teal:        #0891B2;
  --teal-dim:    rgba(8,145,178,.10);
  --shadow-sm:   0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md:   0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
  --shadow-hover:0 8px 24px rgba(0,0,0,.10), 0 3px 8px rgba(0,0,0,.06);
  --radius:      10px;
  --font-head:   'Syne', sans-serif;
  --font-body:   'Outfit', sans-serif;
  --font-mono:   'DM Mono', monospace;
  /* legacy aliases used by existing components */
  --pd-green:           var(--green);
  --text-primary:       var(--text-1);
  --text-secondary:     var(--text-2);
  --text-tertiary:      var(--text-3);
  --bg-primary:         var(--bg);
  --bg-secondary:       var(--surface-2);
  --bg-tertiary:        var(--surface-2);
  --border-primary:     var(--border);
  --border-secondary:   var(--border-2);
  --color-escalation:   var(--amber);
  --status-triggered:   var(--red);
  --status-acknowledged:var(--blue);
  --status-resolved:    var(--green);
}

:root[data-theme="dark"] {
  --bg:        #111110;
  --surface:   #1C1C1A;
  --surface-2: #252523;
  --border:    #2E2E2C;
  --border-2:  #3A3A38;
  --text-1:    #F0F0EE;
  --text-2:    #A0A09A;
  --text-3:    #6A6A64;
  --bg-primary:    #111110;
  --bg-secondary:  #1C1C1A;
  --bg-tertiary:   #252523;
  --border-primary: #2E2E2C;
  --border-secondary: #3A3A38;
  --text-primary:   #F0F0EE;
  --text-secondary: #A0A09A;
  --text-tertiary:  #6A6A64;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text-1);
  font-size: 14px;
  line-height: 1.5;
}

/* ── App shell ── */
.app { display: flex; flex-direction: column; min-height: 100vh; }

/* ── Header ── */
.app-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  height: 52px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.pd-icon { color: var(--green); display: flex; align-items: center; }
.app-header h1 {
  font-family: var(--font-head);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -.01em;
}
.header-spacer { flex: 1; }
.header-controls { display: flex; align-items: center; gap: 8px; }
.ctrl-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 11px;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 7px;
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-2);
  cursor: pointer;
  transition: border-color .15s, color .15s;
}
.ctrl-btn:hover { border-color: var(--green); color: var(--text-1); }
.ctrl-btn:disabled { opacity: .5; cursor: not-allowed; }
.ctrl-btn .chevron { color: var(--text-3); font-size: 10px; margin-left: 2px; }

/* ── Controls (legacy — kept for compatibility) ── */
.controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-wrap: wrap;
}
.controls label { font-size: 12px; font-weight: 600; color: var(--text-2); font-family: var(--font-mono); }
.controls input[type="date"],
.controls select {
  padding: 5px 10px;
  border: 1px solid var(--border-2);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text-1);
  font-size: 13px;
  font-family: var(--font-body);
}

/* ── Tab nav ── */
.tabs {
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: 0 20px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  flex-shrink: 0;
}
.tabs::-webkit-scrollbar { display: none; }
.tab-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 0 14px;
  height: 42px;
  font-family: var(--font-body);
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-3);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color .15s;
  white-space: nowrap;
  margin-bottom: -1px;
}
.tab-btn:hover { color: var(--text-2); }
.tab-btn.tab-active {
  color: var(--green);
  border-bottom-color: var(--green);
  font-weight: 600;
}
.tab-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor;
  opacity: 0;
  transition: opacity .15s;
}
.tab-btn.tab-active .tab-dot { opacity: 1; }

/* ── Home screen ── */
.home-body { padding: 24px 20px; }
.home-intro { margin-bottom: 22px; }
.home-intro h2 {
  font-family: var(--font-head);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -.02em;
  margin-bottom: 4px;
}
.home-intro p { font-size: 13px; color: var(--text-3); }

.menu-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.menu-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 16px 16px;
  cursor: pointer;
  transition: transform .18s cubic-bezier(.34,1.4,.64,1), box-shadow .18s, border-color .18s;
  position: relative;
  overflow: hidden;
  animation: fadeSlideUp .35s cubic-bezier(.22,1,.36,1) both;
}
.menu-card:nth-child(1) { animation-delay: .04s; }
.menu-card:nth-child(2) { animation-delay: .08s; }
.menu-card:nth-child(3) { animation-delay: .12s; }
.menu-card:nth-child(4) { animation-delay: .16s; }
.menu-card:nth-child(5) { animation-delay: .20s; }
.menu-card:nth-child(6) { animation-delay: .24s; }
.menu-card::before {
  content: '';
  position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
  background: var(--card-accent, var(--green));
  border-radius: 0 2px 2px 0;
  transform: scaleY(0);
  transform-origin: center;
  transition: transform .2s cubic-bezier(.34,1.4,.64,1);
}
.menu-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); border-color: var(--border-2); }
.menu-card:hover::before { transform: scaleY(1); }

.card-icon-wrap {
  width: 36px; height: 36px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  background: var(--card-icon-bg, var(--green-dim));
  margin-bottom: 12px;
  font-size: 18px;
}
.menu-card h3 {
  font-family: var(--font-head);
  font-size: 13px; font-weight: 700; letter-spacing: -.01em;
  margin-bottom: 4px;
}
.menu-card p { font-size: 11.5px; color: var(--text-3); line-height: 1.45; margin-bottom: 12px; }
.card-pills { display: flex; flex-wrap: wrap; gap: 4px; }
.pill {
  padding: 2px 7px; border-radius: 100px;
  font-size: 10px; font-weight: 600; letter-spacing: .02em;
  font-family: var(--font-mono);
  background: var(--card-icon-bg, var(--green-dim));
  color: var(--card-accent, var(--green));
}
.card-service   { --card-accent: var(--green);  --card-icon-bg: var(--green-dim); }
.card-team      { --card-accent: var(--blue);   --card-icon-bg: var(--blue-dim); }
.card-responder { --card-accent: var(--violet); --card-icon-bg: var(--violet-dim); }
.card-health    { --card-accent: var(--teal);   --card-icon-bg: var(--teal-dim); }
.card-trends    { --card-accent: var(--amber);  --card-icon-bg: var(--amber-dim); }
.card-comp      { --card-accent: var(--red);    --card-icon-bg: var(--red-dim); }

/* ── KPI bar ── */
.kpi-bar {
  display: flex; gap: 0;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  overflow-x: auto;
}
.kpi-cell {
  flex: 1; min-width: 100px;
  padding: 14px 16px;
  border-right: 1px solid var(--border);
  position: relative;
  animation: fadeSlideUp .3s cubic-bezier(.22,1,.36,1) both;
}
.kpi-cell:nth-child(1) { animation-delay: .05s; }
.kpi-cell:nth-child(2) { animation-delay: .10s; }
.kpi-cell:nth-child(3) { animation-delay: .15s; }
.kpi-cell:nth-child(4) { animation-delay: .20s; }
.kpi-cell:nth-child(5) { animation-delay: .25s; }
.kpi-cell:last-child { border-right: none; }
.kpi-cell::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: var(--cell-color, transparent); opacity: 0; transition: opacity .2s;
}
.kpi-cell:hover::after { opacity: 1; }
.kpi-cell.kpi-warn { --cell-color: var(--amber); }
.kpi-cell.kpi-ok   { --cell-color: var(--green); }

/* Legacy summary-cards compatibility (summary-cards -> kpi-bar) */
.summary-cards { display: flex; gap: 0; border-bottom: 1px solid var(--border); background: var(--surface); overflow-x: auto; }
.summary-card  { flex: 1; min-width: 100px; padding: 14px 16px; border-right: 1px solid var(--border); }
.summary-card:last-child { border-right: none; }

.kpi-label, .summary-label {
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 500;
  color: var(--text-3);
  text-transform: uppercase; letter-spacing: .07em;
  margin-bottom: 4px;
}
.kpi-value, .summary-value {
  font-family: var(--font-mono);
  font-size: 22px; font-weight: 500;
  letter-spacing: -.02em; line-height: 1;
}
.kpi-value.warn { color: var(--amber); }
.kpi-sub, .summary-sub { font-size: 10.5px; color: var(--text-3); margin-top: 3px; }

/* ── Section / analytics ── */
.body { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.analytics-section {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.section-title {
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 500;
  color: var(--text-3);
  text-transform: uppercase; letter-spacing: .08em;
  margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}
.section-count {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 1px 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-3);
}

/* ── Analytics tables ── */
.analytics-table {
  width: 100%; border-collapse: collapse; font-size: 13px;
}
.analytics-table th {
  text-align: left; padding: 6px 10px;
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 500; color: var(--text-3);
  text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid var(--border); white-space: nowrap;
}
.analytics-table td {
  padding: 9px 10px; border-bottom: 1px solid var(--border);
}
.analytics-table tr:last-child td { border-bottom: none; }
.analytics-table tr:hover td { background: var(--surface-2); }

.col-name { font-weight: 600; font-size: 13px; }
.col-num  { text-align: right; }
.col-mono { font-family: var(--font-mono); font-size: 12px; }
.col-warn { color: var(--amber); font-weight: 600; }
.col-ok   { color: var(--green); }

/* Bar cell in tables */
.bar-cell { display: flex; align-items: center; gap: 8px; min-width: 80px; }
.bar-track { flex: 1; max-width: 60px; height: 5px; background: var(--surface-2); border-radius: 3px; overflow: hidden; }
.bar-fill  { height: 100%; background: var(--green); border-radius: 3px; }
.bar-num   { font-family: var(--font-mono); font-size: 12px; }

/* ── Badges ── */
.badge {
  display: inline-flex; align-items: center;
  padding: 2px 8px; border-radius: 100px;
  font-family: var(--font-mono); font-size: 10px; font-weight: 500;
}
.badge-ok   { background: var(--green-dim);  color: var(--green); }
.badge-warn { background: var(--amber-dim);  color: var(--amber); }
.badge-red  { background: var(--red-dim);    color: var(--red); }

/* Risk badges */
.risk-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 100px; font-family: var(--font-mono); font-size: 10px; font-weight: 700; }
.risk-badge.risk-high   { background: var(--red-dim);    color: var(--red); }
.risk-badge.risk-medium { background: var(--amber-dim);  color: var(--amber); }
.risk-badge.risk-low    { background: var(--green-dim);  color: var(--green); }
.analytics-table tr.row-risk-high td   { background: rgba(220,38,38,.04); }
.analytics-table tr.row-risk-medium td { background: rgba(217,119,6,.04); }
:root[data-theme="dark"] .analytics-table tr.row-risk-high td   { background: rgba(220,38,38,.08); }
:root[data-theme="dark"] .analytics-table tr.row-risk-medium td { background: rgba(217,119,6,.08); }

/* ── Fatigue KPI (TeamHealth) ── */
.fatigue-summary {
  display: flex; gap: 0;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  overflow-x: auto;
}
.fatigue-kpi-card {
  flex: 1; min-width: 100px;
  padding: 14px 16px;
  border-right: 1px solid var(--border);
}
.fatigue-kpi-card:last-child { border-right: none; }
.fatigue-kpi-card.fatigue-high   { border-top: 2px solid var(--red); }
.fatigue-kpi-card.fatigue-medium { border-top: 2px solid var(--amber); }
.fatigue-kpi-card.fatigue-low    { border-top: 2px solid var(--green); }

/* ── Percentile section ── */
.percentile-section { border-bottom: 1px solid var(--border); }
.percentile-toggle {
  width: 100%; text-align: left; padding: 8px 20px;
  background: none; border: none; cursor: pointer;
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 500; color: var(--text-3);
  display: flex; align-items: center; gap: 6px;
  text-transform: uppercase; letter-spacing: .07em;
}
.percentile-toggle:hover { color: var(--text-2); background: var(--surface-2); }
.percentile-grid {
  display: grid; grid-template-columns: repeat(4, 1fr) repeat(4, 1fr);
  gap: 8px; padding: 8px 20px 12px;
}
.percentile-cell {
  padding: 8px 10px; background: var(--surface-2);
  border: 1px solid var(--border); border-radius: 6px;
}
.percentile-label { font-family: var(--font-mono); font-size: 10px; font-weight: 500; color: var(--text-3); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 2px; }
.percentile-value { font-family: var(--font-mono); font-size: 15px; font-weight: 500; }

/* ── Trends ── */
.trends-tab   { padding: 12px 16px; display: flex; flex-direction: column; gap: 16px; }
.trends-empty { padding: 32px 16px; text-align: center; color: var(--text-3); font-size: 14px; }
.trend-card   { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; }
.trend-card-title { font-family: var(--font-mono); font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: .07em; color: var(--text-3); margin-bottom: 8px; }
.trend-chart  { width: 100%; height: auto; display: block; }
.chart-empty  { font-size: 12px; color: var(--text-3); padding: 8px 0; }

/* ── Compensation page ── */
.comp-page { display: flex; flex-direction: column; }
.comp-empty { padding: 40px 20px; text-align: center; color: var(--text-3); font-size: 14px; }

/* ── States ── */
.loading, .empty-state, .error-state {
  text-align: center; padding: 40px 20px; color: var(--text-2);
  font-family: var(--font-body);
}
.error-state { color: var(--red); }

/* ── Buttons ── */
.btn { padding: 7px 14px; border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid transparent; font-family: var(--font-body); }
.btn-primary { background: var(--green); color: #fff; border-color: var(--green); }
.btn-primary:hover:not(:disabled) { background: #059030; }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; }
.btn-sm { padding: 5px 10px; font-size: 12px; }

/* ── Animations ── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Dark mode overrides ── */
:root[data-theme="dark"] .analytics-table th { background: var(--surface); }
:root[data-theme="dark"] .controls input[type="date"],
:root[data-theme="dark"] .controls select { background: var(--surface-2); border-color: var(--border); color: var(--text-1); }
:root[data-theme="dark"] .ctrl-btn { background: var(--surface); color: var(--text-2); border-color: var(--border-2); }
:root[data-theme="dark"] .app-header,
:root[data-theme="dark"] .tabs,
:root[data-theme="dark"] .kpi-bar,
:root[data-theme="dark"] .fatigue-summary { background: var(--surface); }

/* Sortable table headers */
.th-sortable { cursor: pointer; user-select: none; }
.th-sortable:hover { color: var(--text-1); }
.th-active { color: var(--green) !important; }

/* service-table alias */
.service-breakdown { padding: 16px 20px; border-bottom: 1px solid var(--border); }
```

- [ ] **Step 2: Build to verify no CSS issues**

```bash
cd mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npm run build 2>&1 | tail -20
```

Expected: build succeeds (no parse errors from the CSS file).

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/operations-intelligence/src/styles.css
git commit -m "feat(ops-intelligence): replace styles with Syne/DM Mono/Outfit design system"
```

---

## Task 2: Create HomePage component

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/HomePage.tsx`

- [ ] **Step 1: Create HomePage.tsx**

```tsx
import type { Page } from "../mcp-app";

interface MenuCardProps {
  icon: string;
  title: string;
  description: string;
  pills: string[];
  page: Page;
  cardClass: string;
  onNavigate: (page: Page) => void;
}

function MenuCard({ icon, title, description, pills, page, cardClass, onNavigate }: MenuCardProps) {
  return (
    <div
      className={`menu-card ${cardClass}`}
      onClick={() => onNavigate(page)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onNavigate(page); }}
    >
      <div className="card-icon-wrap">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <div className="card-pills">
        {pills.map((p) => <span key={p} className="pill">{p}</span>)}
      </div>
    </div>
  );
}

interface HomePageProps {
  onNavigate: (page: Page) => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div className="home-body">
      <div className="home-intro">
        <h2>What would you like to explore?</h2>
        <p>Select a section to dive into your operational data for the selected period.</p>
      </div>
      <div className="menu-grid">
        <MenuCard
          icon="📊"
          title="Service Metrics"
          description="Incident volume, MTTA, MTTR and uptime per service."
          pills={["MTTA", "MTTR", "Uptime"]}
          page="service"
          cardClass="card-service"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="👥"
          title="Team Metrics"
          description="Incident volume, escalations and response times per team."
          pills={["Incidents", "Escalations"]}
          page="team"
          cardClass="card-team"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="🧑‍💻"
          title="Responder Metrics"
          description="On-call hours, ack rates and interruption load per responder."
          pills={["Load", "Risk", "Hours"]}
          page="responder"
          cardClass="card-responder"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="💙"
          title="Team Health"
          description="Fatigue signals, sleep-hour interruptions and burnout risk scoring."
          pills={["Fatigue", "Burnout"]}
          page="teamHealth"
          cardClass="card-health"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="📈"
          title="Trends"
          description="Weekly incident volume, MTTA and MTTR trend charts over time."
          pills={["Charts", "Weekly"]}
          page="trends"
          cardClass="card-trends"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="💰"
          title="Oncall Compensation"
          description="Per-responder on-call hours, interruptions and outside-hours breakdown."
          pills={["Hours", "Shifts", "Risk"]}
          page="compensation"
          cardClass="card-comp"
          onNavigate={onNavigate}
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/operations-intelligence/src/components/HomePage.tsx
git commit -m "feat(ops-intelligence): add HomePage card grid component"
```

---

## Task 3: Create CompensationPage component

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/CompensationPage.tsx`

- [ ] **Step 1: Create CompensationPage.tsx**

```tsx
import type { ResponderMetric } from "../api";
import { fmtMin } from "../utils";

interface CompensationPageProps {
  metrics: ResponderMetric[];
}

function fmtHours(h: number): string {
  return `${h}h`;
}

export function CompensationPage({ metrics }: CompensationPageProps) {
  if (metrics.length === 0) {
    return <div className="comp-empty">No responder data available for this period.</div>;
  }

  const totalOnCallHours = metrics.reduce((s, r) => s + r.onCallHours, 0);
  const avgOnCallHours = metrics.length > 0
    ? Math.round((totalOnCallHours / metrics.length) * 10) / 10
    : 0;
  const totalSleepInt = metrics.reduce((s, r) => s + r.sleepInterruptions, 0);
  const highRiskCount = metrics.filter((r) => r.riskLevel === "high").length;

  const sorted = [...metrics].sort((a, b) => b.onCallHours - a.onCallHours);

  return (
    <div className="comp-page">
      {/* KPI bar */}
      <div className="kpi-bar">
        <div className="kpi-cell kpi-ok">
          <div className="kpi-label">Responders</div>
          <div className="kpi-value">{metrics.length}</div>
          <div className="kpi-sub">with on-call data</div>
        </div>
        <div className="kpi-cell">
          <div className="kpi-label">Total On-Call</div>
          <div className="kpi-value">{fmtHours(totalOnCallHours)}</div>
          <div className="kpi-sub">hours this period</div>
        </div>
        <div className="kpi-cell">
          <div className="kpi-label">Avg Per Responder</div>
          <div className="kpi-value">{fmtHours(avgOnCallHours)}</div>
          <div className="kpi-sub">on-call hours</div>
        </div>
        <div className={`kpi-cell${totalSleepInt > 0 ? " kpi-warn" : " kpi-ok"}`}>
          <div className="kpi-label">Sleep Interruptions</div>
          <div className={`kpi-value${totalSleepInt > 0 ? " warn" : ""}`}>{totalSleepInt}</div>
          <div className="kpi-sub">total this period</div>
        </div>
        <div className={`kpi-cell${highRiskCount > 0 ? " kpi-warn" : " kpi-ok"}`}>
          <div className="kpi-label">High Risk</div>
          <div className={`kpi-value${highRiskCount > 0 ? " warn" : ""}`}>{highRiskCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
      </div>

      {/* Table */}
      <div className="analytics-section">
        <div className="section-title">
          Responder On-Call Summary
          <span className="section-count">{metrics.length}</span>
        </div>
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Responder</th>
              <th className="col-num">On-Call Hrs</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">Sleep Int.</th>
              <th className="col-num">Off-Hr Int.</th>
              <th className="col-num">Engaged Time</th>
              <th className="col-num">Risk</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r) => (
              <tr key={r.id} className={r.riskLevel !== "low" ? `row-risk-${r.riskLevel}` : ""}>
                <td className="col-name">
                  {r.name}
                  {r.teamName && <span className="kpi-sub"> · {r.teamName}</span>}
                </td>
                <td className="col-num col-mono">{fmtHours(r.onCallHours)}</td>
                <td className="col-num">{r.totalIncidents}</td>
                <td className={`col-num${r.sleepInterruptions > 0 ? " col-warn" : " col-ok"}`}>
                  {r.sleepInterruptions}
                </td>
                <td className="col-num">{r.offHourInterruptions}</td>
                <td className="col-num col-mono">{fmtMin(r.engagedMinutes)}</td>
                <td className="col-num">
                  <span className={`risk-badge risk-${r.riskLevel}`}>
                    {r.riskLevel.charAt(0).toUpperCase() + r.riskLevel.slice(1)}
                  </span>
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

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/operations-intelligence/src/components/CompensationPage.tsx
git commit -m "feat(ops-intelligence): add CompensationPage component"
```

---

## Task 4: Rewrite mcp-app.tsx with Page state + tab nav

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/mcp-app.tsx`

This is the largest change — it replaces the tab state with a `Page` type, adds the persistent tab nav, and wires up all pages.

- [ ] **Step 1: Replace mcp-app.tsx entirely**

```tsx
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchOpsData, type OpsData } from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { SummaryCards } from "./components/SummaryCards";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { TeamBreakdown } from "./components/TeamBreakdown";
import { ResponderLoad } from "./components/ResponderLoad";
import { TrendsTab } from "./components/TrendsTab";
import { TeamHealth } from "./components/TeamHealth";
import { PercentileSection } from "./components/PercentileSection";
import { HomePage } from "./components/HomePage";
import { CompensationPage } from "./components/CompensationPage";

export type Page = "home" | "service" | "team" | "responder" | "teamHealth" | "trends" | "compensation";

const TABS: { id: Page; label: string }[] = [
  { id: "home",         label: "Home" },
  { id: "service",      label: "Service Metrics" },
  { id: "team",         label: "Team Metrics" },
  { id: "responder",    label: "Responder" },
  { id: "teamHealth",   label: "Team Health" },
  { id: "trends",       label: "Trends" },
  { id: "compensation", label: "Compensation" },
];

function getDefaultSince(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0]!;
}

function getToday(): string {
  return new Date().toISOString().split("T")[0]!;
}

function detectTheme(): "dark" | "light" {
  const param = new URLSearchParams(window.location.search).get("theme");
  if (param === "dark") return "dark";
  if (param === "light") return "light";
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Operations Intelligence", version: "3.0.0" },
    capabilities: {},
  });
  const mockMode = import.meta.env.VITE_MOCK === "true";

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [page, setPage] = useState<Page>("home");
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [selectedTeam, setSelectedTeam] = useState<string>("");

  const [data, setData] = useState<OpsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const load = useCallback(async () => {
    if (!app && !mockMode) return;
    setLoading(true);
    setError(null);
    try {
      const d = await fetchOpsData(
        app ?? ({} as any),
        new Date(since).toISOString(),
        new Date(until + "T23:59:59").toISOString(),
        selectedTeam || null
      );
      setData(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [app, since, until, selectedTeam]);

  useEffect(() => {
    load();
  }, [load]);

  const displayError = mockMode ? null : (connectionError?.message ?? error);

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="app-header">
        <span className="pd-icon"><PagerDutyLogo size={22} /></span>
        <h1>Operations Intelligence</h1>
        <div className="header-spacer" />
        <div className="header-controls">
          <select
            className="ctrl-btn"
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.currentTarget.value)}
          >
            <option value="">All teams</option>
            {(data?.teams ?? []).map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          <input
            type="date"
            className="ctrl-btn"
            value={since}
            onChange={(e) => setSince(e.currentTarget.value)}
          />
          <input
            type="date"
            className="ctrl-btn"
            value={until}
            onChange={(e) => setUntil(e.currentTarget.value)}
          />
          <button className="btn btn-primary btn-sm" onClick={load} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
        </div>
      </header>

      {/* ── Tab nav ── */}
      <nav className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn${page === tab.id ? " tab-active" : ""}`}
            onClick={() => setPage(tab.id)}
          >
            {page === tab.id && <span className="tab-dot" />}
            {tab.label}
          </button>
        ))}
      </nav>

      {/* ── Error banner ── */}
      {displayError && <div className="error-state">{displayError}</div>}

      {/* ── Loading ── */}
      {loading && !data && <div className="loading">Loading operational data…</div>}

      {/* ── Page content ── */}
      {!loading || data ? (
        <>
          {page === "home" && <HomePage onNavigate={setPage} />}

          {page === "service" && data && (
            <div className="body">
              <SummaryCards data={data} />
              <PercentileSection aggregated={data.aggregated} />
              <ServiceBreakdown metrics={data.serviceMetrics} />
            </div>
          )}

          {page === "team" && data && (
            <div className="body">
              <TeamBreakdown metrics={data.teamMetrics} />
            </div>
          )}

          {page === "responder" && data && (
            <div className="body">
              <ResponderLoad metrics={data.responderMetrics} />
            </div>
          )}

          {page === "teamHealth" && data && (
            <TeamHealth metrics={data.responderMetrics} teamMetrics={data.teamMetrics} />
          )}

          {page === "trends" && data && (
            <TrendsTab trendsData={data.trendsData} />
          )}

          {page === "compensation" && data && (
            <CompensationPage metrics={data.responderMetrics} />
          )}

          {page !== "home" && !data && !loading && (
            <div className="empty-state">No data — adjust date range and refresh.</div>
          )}
        </>
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 2: Build and verify TypeScript**

```bash
cd mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npm run build 2>&1 | tail -30
```

Expected: `✓ built in` with no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/operations-intelligence/src/mcp-app.tsx
git commit -m "feat(ops-intelligence): add Page state, persistent tab nav, and home menu"
```

---

## Task 5: Update TrendsTab CSS variable references

The TrendsTab SVG charts reference old CSS variables (`--border-secondary`, `--text-secondary`) that are now aliased but the SVG `fill` attribute doesn't resolve CSS vars from SVG text elements in all browsers. Update to use the new token names.

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/components/TrendsTab.tsx`

- [ ] **Step 1: Update CSS variable references in TrendsTab**

In `TrendsTab.tsx`, replace all `var(--border-secondary)` → `var(--border-2)` and `var(--text-secondary)` → `var(--text-2)`. Also update chart color references:

```tsx
// In BarChart component, line with stroke:
stroke="var(--border-2)"

// In LineChart component:
stroke="var(--border-2)"

// In TrendsTab return, update chart colors:
<BarChart points={trendsData.points} getValue={(p) => p.totalIncidents} color="var(--red)" yLabel="Incidents" />
<LineChart points={trendsData.points} getValue={(p) => p.mttaMinutes} color="var(--blue)" yLabel="min" />
<LineChart points={trendsData.points} getValue={(p) => p.mttrMinutes} color="var(--green)" yLabel="min" />
<BarChart points={trendsData.points} getValue={(p) => p.totalInterruptions} color="var(--amber)" yLabel="Count" />
```

The full updated file:

```tsx
import type { TrendsData, TrendPoint } from "../api";

interface TrendsTabProps {
  trendsData: TrendsData | null;
}

const CHART_W = 600;
const CHART_H = 120;
const PAD = { top: 10, right: 16, bottom: 28, left: 44 };

function plotW() { return CHART_W - PAD.left - PAD.right; }
function plotH() { return CHART_H - PAD.top - PAD.bottom; }

function formatWeek(weekStart: string): string {
  const d = new Date(weekStart + "T00:00:00");
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

interface BarChartProps {
  points: TrendPoint[];
  getValue: (p: TrendPoint) => number;
  color: string;
  yLabel: string;
}

function BarChart({ points, getValue, color, yLabel }: BarChartProps) {
  if (points.length === 0) return <div className="chart-empty">No data</div>;
  const values = points.map(getValue);
  const maxVal = Math.max(...values, 1);
  const barW = plotW() / points.length * 0.6;
  const barGap = plotW() / points.length;

  return (
    <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} className="trend-chart" preserveAspectRatio="xMidYMid meet">
      <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + plotH()} stroke="var(--border-2)" strokeWidth="1" />
      <text x={8} y={PAD.top + plotH() / 2} fontSize="10" fill="var(--text-2)" textAnchor="middle" transform={`rotate(-90, 8, ${PAD.top + plotH() / 2})`}>{yLabel}</text>
      <text x={PAD.left - 4} y={PAD.top + plotH()} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">0</text>
      <text x={PAD.left - 4} y={PAD.top} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">{maxVal}</text>
      {points.map((p, i) => {
        const val = getValue(p);
        const barH = (val / maxVal) * plotH();
        const x = PAD.left + i * barGap + (barGap - barW) / 2;
        const y = PAD.top + plotH() - barH;
        return (
          <g key={p.weekStart}>
            <rect x={x} y={y} width={barW} height={barH} fill={color} rx="2" opacity="0.85" />
            <text x={x + barW / 2} y={PAD.top + plotH() + 14} fontSize="9" fill="var(--text-2)" textAnchor="middle">{formatWeek(p.weekStart)}</text>
          </g>
        );
      })}
    </svg>
  );
}

interface LineChartProps {
  points: TrendPoint[];
  getValue: (p: TrendPoint) => number | null;
  color: string;
  yLabel: string;
}

function LineChart({ points, getValue, color, yLabel }: LineChartProps) {
  const valid = points.filter((p) => getValue(p) !== null);
  if (valid.length === 0) return <div className="chart-empty">No data</div>;
  const values = valid.map((p) => getValue(p) as number);
  const maxVal = Math.max(...values, 1);
  const minVal = Math.min(...values, 0);
  const range = maxVal - minVal || 1;

  function xOf(i: number) { return PAD.left + (i / (points.length - 1 || 1)) * plotW(); }
  function yOf(val: number) { return PAD.top + plotH() - ((val - minVal) / range) * plotH(); }

  const polyPoints = points
    .map((p, i) => { const v = getValue(p); return v !== null ? `${xOf(i)},${yOf(v)}` : null; })
    .filter(Boolean)
    .join(" ");

  return (
    <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} className="trend-chart" preserveAspectRatio="xMidYMid meet">
      <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + plotH()} stroke="var(--border-2)" strokeWidth="1" />
      <text x={8} y={PAD.top + plotH() / 2} fontSize="10" fill="var(--text-2)" textAnchor="middle" transform={`rotate(-90, 8, ${PAD.top + plotH() / 2})`}>{yLabel}</text>
      <text x={PAD.left - 4} y={PAD.top + plotH()} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">{minVal}</text>
      <text x={PAD.left - 4} y={PAD.top} fontSize="9" fill="var(--text-2)" textAnchor="end" dominantBaseline="middle">{maxVal}</text>
      <polyline points={polyPoints} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {points.map((p, i) => {
        const v = getValue(p);
        return (
          <g key={p.weekStart}>
            {v !== null && <circle cx={xOf(i)} cy={yOf(v)} r="3.5" fill={color} />}
            <text x={xOf(i)} y={PAD.top + plotH() + 14} fontSize="9" fill="var(--text-2)" textAnchor="middle">{formatWeek(p.weekStart)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function TrendsTab({ trendsData }: TrendsTabProps) {
  if (!trendsData || trendsData.points.length === 0) {
    return <div className="trends-empty">No trend data available for this period.</div>;
  }
  return (
    <div className="trends-tab">
      <div className="trend-card">
        <div className="trend-card-title">Incident Volume (per week)</div>
        <BarChart points={trendsData.points} getValue={(p) => p.totalIncidents} color="var(--red)" yLabel="Incidents" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">MTTA — Mean Time to Ack (minutes)</div>
        <LineChart points={trendsData.points} getValue={(p) => p.mttaMinutes} color="var(--blue)" yLabel="min" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">MTTR — Mean Time to Resolve (minutes)</div>
        <LineChart points={trendsData.points} getValue={(p) => p.mttrMinutes} color="var(--green)" yLabel="min" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">Interruptions (per week)</div>
        <BarChart points={trendsData.points} getValue={(p) => p.totalInterruptions} color="var(--amber)" yLabel="Count" />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Build and verify**

```bash
cd mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npm run build 2>&1 | tail -20
```

Expected: `✓ built in` with no errors.

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/operations-intelligence/src/components/TrendsTab.tsx
git commit -m "feat(ops-intelligence): update TrendsTab to use new CSS token names"
```

---

## Task 6: Full build + mock mode smoke test

**Files:** No code changes — verification only.

- [ ] **Step 1: Full build**

```bash
cd mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npm run build 2>&1
```

Expected: output ends with `✓ built in Xs` — zero TypeScript errors, zero warnings about missing exports.

- [ ] **Step 2: Run mock dev server**

```bash
cd mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && VITE_MOCK=true npm run dev 2>&1 &
sleep 3
echo "Dev server started"
```

- [ ] **Step 3: Take screenshot of home screen**

```bash
source ~/.nvm/nvm.sh && nvm use && npx playwright screenshot http://localhost:5173 /tmp/ops-home.png --wait-for-timeout 2000
```

Open `/tmp/ops-home.png` and verify: PD green header, 3-column card grid with 6 colored cards, persistent tab bar.

- [ ] **Step 4: Take screenshot of Service Metrics page**

```bash
npx playwright screenshot "http://localhost:5173?page=service" /tmp/ops-service.png --wait-for-timeout 2000
```

Expected: 5-cell KPI bar with DM Mono numbers, analytics table below.

> Note: if the app doesn't respond to `?page=` param, use Playwright to click the "Service Metrics" tab instead. The screenshot step is to visually confirm the redesign looks correct — not a functional test.

- [ ] **Step 5: Kill dev server and run build-all**

```bash
pkill -f "vite.*operations-intelligence" 2>/dev/null || true
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server && source ~/.nvm/nvm.sh && nvm use && bash mcp-apps/build-all.sh 2>&1 | grep -E "(ops|built|error|Error)" | head -20
```

Expected: `operations-intelligence` builds without errors and the HTML bundle is copied to `pagerduty_mcp/`.

- [ ] **Step 6: Commit**

```bash
git add pagerduty_mcp/operations_intelligence_view.html
git commit -m "feat(ops-intelligence): rebuild HTML bundle with home menu + compensation page"
```

---

## Self-Review Against Spec

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| Home screen with 3-column card grid | Task 2 (HomePage) + Task 4 (mcp-app.tsx) |
| Persistent tab bar (7 tabs) | Task 4 (mcp-app.tsx) |
| Page navigation: card click → page | Task 2 (HomePage `onNavigate`) |
| Date/team filter in header, shared | Task 4 (mcp-app.tsx header controls) |
| Service Metrics page | Task 4 (page === "service") |
| Team Metrics page | Task 4 (page === "team") |
| Responder Metrics page | Task 4 (page === "responder") |
| Team Health page | Task 4 (page === "teamHealth") |
| Trends page (charts only) | Task 4 (page === "trends") |
| Oncall Compensation page (new) | Task 3 (CompensationPage) + Task 4 |
| Compensation reuses responderMetrics | Task 3 (props: `metrics: ResponderMetric[]`) |
| Syne + DM Mono + Outfit fonts | Task 1 (styles.css @import) |
| Color-coded cards with accents | Task 1 (CSS) + Task 2 (cardClass props) |
| KPI bar (Bloomberg-style) | Task 1 (CSS `.kpi-bar`, `.kpi-cell`) |
| Stagger animations | Task 1 (CSS `animation-delay`) |
| Dark mode token mapping | Task 1 (`:root[data-theme="dark"]`) |
| CSS variable legacy aliases | Task 1 (ensures existing components work) |
| Build output registered in server.py | No change needed (same app, same HTML path) |

All spec requirements covered. No placeholders. Type `Page` exported from `mcp-app.tsx` and consumed by `HomePage.tsx` — consistent across tasks.
