# Create PagerDuty MCP App Skill

**Version**: 1.0.0
**Author**: PagerDuty Professional Services
**Category**: Development
**Tags**: mcp, pagerduty, ui, react, visualization

## Description

Create or modify PagerDuty MCP Apps using the Incident Command Center as a golden template. This skill provides scaffolding, architecture guidance, and best practices for building interactive UIs that integrate with PagerDuty's MCP server tools.

## Usage

```bash
# Create a new PagerDuty MCP App
/create-pagerduty-mcp-app <app-name> [options]

# Examples
/create-pagerduty-mcp-app service-dashboard
/create-pagerduty-mcp-app oncall-calendar --based-on incident-command-center
/create-pagerduty-mcp-app team-analytics --tools list_teams,list_services
```

## Options

- `--based-on <template>` - Use existing app as template (default: incident-command-center)
- `--tools <tool1,tool2,...>` - MCP tools the app will use
- `--description "<text>"` - Brief description of the app
- `--features <feature1,feature2,...>` - Features to include (modals, dropdowns, charts, etc.)

## Golden Template: Incident Command Center

The Incident Command Center is the reference implementation with:

### ✅ Architecture Excellence
- **No wrapper tools** - Calls existing MCP tools directly via `app.callServerTool()`
- **Centralized API layer** - `src/api.ts` with typed functions
- **Component modularity** - Reusable components (ActionsDropdown, modals, etc.)
- **Tool-Resource binding** - Python trigger tool + HTML resource pattern

### ✅ UX/UI Best Practices
- **PagerDuty branding** - Official logo and design system
- **Slack-style actions** - Primary buttons + "More actions" dropdown
- **Automatic dark mode** - Syncs with VS Code theme
- **Professional styling** - Clean, modern, accessible design
- **Responsive layout** - Works in different container sizes
- **Dynamic sizing** - Requests appropriate space via size-changed notifications

### ✅ Technical Implementation
- **React + TypeScript** - Type-safe component architecture
- **Vite bundling** - Single HTML file with inlined assets
- **CSS variables** - Theme-aware styling system
- **Error handling** - Graceful degradation and user feedback
- **Loading states** - Clear feedback during async operations
- **Event propagation** - Proper stopPropagation for nested interactions

### ✅ Feature Set
- **Real-time data** - Auto-refresh with configurable intervals
- **Quick actions** - Acknowledge, Resolve from card
- **Action dropdown** - Add Note, Run Workflow, Change Priority, Escalate
- **Details modal** - Comprehensive incident view with tabs
- **Timeline view** - All events in chronological order
- **Alert inspector** - Split-pane alert viewer
- **Escalation panel** - Policy selection and escalation
- **Notes thread** - Add and view notes
- **Priority management** - Change priority (P1-P5)
- **Workflow execution** - Start incident workflows

## Skill Behavior

### When Creating New App:

1. **Analyze Requirements**
   - What data to display (incidents, services, schedules, etc.)
   - What actions users need (acknowledge, escalate, create, etc.)
   - What MCP tools are available

2. **Scaffold Structure**
   ```
   mcp-apps/<app-name>/
   ├── src/
   │   ├── mcp-app.tsx           # Main component
   │   ├── api.ts                # MCP tool calls
   │   ├── styles.css            # Theme-aware styling
   │   ├── components/           # Reusable components
   │   │   ├── <Feature>Modal.tsx
   │   │   ├── ActionsDropdown.tsx (from template)
   │   │   └── PagerDutyLogo.tsx (from template)
   │   └── assets/
   │       └── pagerduty-icon.svg
   ├── server.ts                 # MCP server (optional)
   ├── main.ts                   # Entry point (optional)
   ├── package.json
   ├── tsconfig.json
   ├── vite.config.ts
   └── README.md
   ```

3. **Copy Golden Template Patterns**
   - API layer with proper tool call wrapping
   - Dark mode CSS variables
   - Component structure
   - Error handling patterns
   - Loading states
   - Event propagation fixes

4. **Generate Python Server Integration**
   ```python
   # In pagerduty_mcp/server.py
   @mcp_instance.tool(
       meta={
           "ui": {"resourceUri": f"ui://{app_name}/view.html"},
           "ui/resourceUri": f"ui://{app_name}/view.html",
       }
   )
   def <app_name>() -> list[TextContent]:
       """<App Description>"""
       return [TextContent(type="text", text="<App> UI initialized.")]

   @mcp_instance.resource(
       f"ui://{app_name}/view.html",
       mime_type="text/html",
       description="<App Description>"
   )
   def <app_name>_view() -> str:
       html_path = pathlib.Path(__file__).parent / f"{app_name}_view.html"
       return html_path.read_text(encoding="utf-8")
   ```

5. **Create Build Scripts**
   - Copy from incident-command-center
   - Update paths and names
   - Include in `build-all.sh`

### When Modifying Existing App:

1. **Analyze Current Implementation**
   - Read existing code
   - Identify deviations from golden template
   - Find potential improvements

2. **Suggest Improvements**
   - Compare against Incident Command Center
   - Identify missing patterns (dark mode, error handling, etc.)
   - Suggest architectural improvements

3. **Apply Changes**
   - Update to match golden template patterns
   - Maintain existing functionality
   - Add missing features
   - Improve styling and UX

## Checklist for New Apps

### Architecture Compliance
- [ ] Python server has ONLY trigger tool + resource (no wrappers)
- [ ] React app calls existing MCP tools via `app.callServerTool()`
- [ ] Tool arguments wrapped with parameter names (e.g., `query_model`)
- [ ] Response extraction handles both `data.response` and direct data
- [ ] Error states handled gracefully

### UI/UX Requirements
- [ ] PagerDuty logo in header (use official logo)
- [ ] Dark mode support with CSS variables
- [ ] Theme detection from VS Code
- [ ] Professional PagerDuty design system colors
- [ ] Responsive layout (works in different container sizes)
- [ ] Dynamic sizing (requests appropriate space)
- [ ] Loading states for all async operations
- [ ] Error messages for failed operations

### Component Patterns
- [ ] Centralized API layer (`src/api.ts`)
- [ ] Reusable components (dropdowns, modals, etc.)
- [ ] Event propagation handled correctly (`stopPropagation`)
- [ ] TypeScript interfaces for all data types
- [ ] Proper cleanup in useEffect hooks

### Action Buttons
- [ ] Primary actions as buttons (most common operations)
- [ ] "More actions" dropdown for secondary actions
- [ ] "Details" button for comprehensive view
- [ ] All buttons same height (36px)
- [ ] Slack-style bordered button design

### Modal Patterns
- [ ] Modal overlay with backdrop
- [ ] Click outside to close
- [ ] Close button (×) in header
- [ ] Summary section with incident info
- [ ] Action button in footer
- [ ] Error states displayed
- [ ] Loading states shown
- [ ] Auto-refresh parent on success

### Styling Standards
- [ ] CSS variables for theming (--bg-primary, --text-primary, etc.)
- [ ] Dark mode overrides for components
- [ ] Consistent spacing and padding
- [ ] Status badges with clear colors
- [ ] Professional typography (system fonts)
- [ ] Custom scrollbars for better UX

## Examples

### Example 1: Service Health Dashboard
```bash
/create-pagerduty-mcp-app service-health-dashboard \
  --tools list_services,list_incidents,list_teams \
  --description "Real-time service health monitoring" \
  --features grid,filtering,search,details-modal
```

**Creates**:
- Grid layout showing services
- Health status indicators
- Filter by team
- Search services
- Click service for incident history

### Example 2: On-Call Calendar
```bash
/create-pagerduty-mcp-app oncall-calendar \
  --tools list_schedules,list_oncalls,list_users \
  --description "Visual on-call schedule calendar" \
  --features calendar,timeline,user-cards
```

**Creates**:
- Calendar view of schedules
- On-call user highlights
- Override management
- Schedule details modal

### Example 3: Team Analytics
```bash
/create-pagerduty-mcp-app team-analytics \
  --tools list_teams,list_incidents,list_users \
  --description "Team performance and incident analytics" \
  --features charts,metrics,filters,export
```

**Creates**:
- Team performance charts
- Incident metrics
- Filtering by date range
- Export capabilities

## Golden Template Location

**Path**: `/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/incident-command-center/`

**Key Files to Reference**:
- `src/mcp-app.tsx` - Main component with theme detection, sizing, modals
- `src/api.ts` - API layer with all tool call patterns
- `src/styles.css` - Complete dark mode CSS system
- `src/components/ActionsDropdown.tsx` - Reusable dropdown pattern
- `src/components/EscalationModal.tsx` - Modal pattern example
- `src/components/PriorityModal.tsx` - Dropdown selector pattern
- `src/components/WorkflowModal.tsx` - Async data loading pattern
- `package.json` - Build configuration
- `vite.config.ts` - Vite single-file plugin config

## Validation Criteria

**Before marking app as complete, verify**:

✅ All MCP tool calls successful (0 errors in console)
✅ Dark mode works (test theme switching)
✅ All buttons same size and aligned
✅ Modals don't trigger parent clicks
✅ Loading states show during async ops
✅ Error states handled gracefully
✅ Layout fits in VS Code container
✅ Scrolling only where intended
✅ Status badges visible in both themes
✅ All user interactions functional

## Best Practices Learned

### From Incident Command Center Development:

1. **Parameter Wrapping**: FastMCP requires arguments wrapped with parameter name when function takes Pydantic model
   ```typescript
   // Wrong
   arguments: { status: [...], limit: 100 }

   // Correct
   arguments: { query_model: { status: [...], limit: 100 } }
   ```

2. **Event Propagation**: Stop propagation at multiple levels for nested components
   ```typescript
   <div onClick={(e) => e.stopPropagation()}>
     <Component />
   </div>
   ```

3. **Dark Mode**: Manual theme detection more reliable than hooks
   ```typescript
   const theme = context?.theme || 'light';
   document.documentElement.setAttribute('data-theme', theme);
   ```

4. **Dynamic Sizing**: Request space for modals
   ```typescript
   app.notification({
     method: "ui/notifications/size-changed",
     params: { height: 700 }
   });
   ```

5. **CSS Specificity**: Use specific selectors to avoid conflicts
   ```css
   .urgency-badge.urgency-high { /* Not just .urgency-high */ }
   ```

6. **Missing Fields**: Add fields to Python models as needed
   ```python
   class Incident(BaseModel):
       urgency: Urgency = Field(default="high")
       alert_counts: AlertCounts | None = None
       priority: PriorityReference | None = None
   ```

## Maintenance Notes

**Keep Golden Template Updated**:
- When adding new features to Incident Command Center, update skill documentation
- When finding new patterns or best practices, document them here
- When fixing bugs, ensure fixes are reflected in template

**Template Evolution**:
- Current version: v1.0 (Iteration 14)
- Includes: Full action set, dark mode, priority system, workflows
- Status: Production ready
- Last updated: 2026-02-04

## Success Metrics

**A well-built PagerDuty MCP App should have**:
- 🎯 0 wrapper tools (calls existing tools only)
- 🎯 100% tool call success rate
- 🎯 Dark mode support
- 🎯 <3 second load time
- 🎯 Professional PagerDuty design
- 🎯 All user interactions functional
- 🎯 Proper error handling
- 🎯 Mobile-responsive layout

---

**Template Repository**: `/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/incident-command-center/`
**Documentation**: See `.claude/iteration-*.md` for development history and patterns
**Status**: Golden template validated through 14 iterations
