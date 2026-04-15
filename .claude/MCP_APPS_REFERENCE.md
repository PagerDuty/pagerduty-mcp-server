# PagerDuty MCP Apps - Quick Reference

**Golden Template**: Incident Command Center
**Status**: Production Ready ✅
**Location**: `mcp-apps/incident-command-center/`

## Essential Patterns

### 1. Python Server Structure

```python
# In pagerduty_mcp/server.py

APP_URI = "ui://app-name/view.html"

@mcp_instance.tool(
    meta={
        "ui": {"resourceUri": APP_URI},
        "ui/resourceUri": APP_URI,  # legacy
    }
)
def app_name() -> list[TextContent]:
    """App description. UI calls existing MCP tools."""
    return [TextContent(type="text", text="UI initialized.")]

@mcp_instance.resource(APP_URI, mime_type="text/html")
def app_name_view() -> str:
    html_path = pathlib.Path(__file__).parent / "app_name_view.html"
    return html_path.read_text(encoding="utf-8")
```

### 2. Tool Call Patterns

```typescript
// Pydantic model parameters: MUST wrap with parameter name
await app.callServerTool({
  name: "list_incidents",
  arguments: {
    query_model: { status: ["triggered"], limit: 100 }
  }
});

// Simple parameters: Pass directly
await app.callServerTool({
  name: "get_incident",
  arguments: { incident_id: "P123" }
});

// Mixed parameters
await app.callServerTool({
  name: "list_alerts_from_incident",
  arguments: {
    incident_id: "P123",
    query_model: { limit: 50 }
  }
});
```

### 3. Dark Mode Implementation

```typescript
// Theme detection
useEffect(() => {
  if (app) {
    const context = app.getHostContext();
    const theme = context?.theme || 'light';
    document.documentElement.setAttribute('data-theme', theme);

    app.onhostcontextchanged = (params) => {
      if (params.theme) {
        document.documentElement.setAttribute('data-theme', params.theme);
      }
    };
  }
}, [app]);
```

```css
/* CSS Variables */
:root {
  --bg-primary: #ffffff;
  --text-primary: #1d1d1f;
}

:root[data-theme="dark"] {
  --bg-primary: #1e1e1e;
  --text-primary: #d4d4d4;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
}
```

### 4. Response Extraction

```typescript
function extractData<T>(result: CallToolResult): T | null {
  if (result.isError) {
    const errorText = result.content?.find(c => c.type === "text")?.text;
    console.error("[API] Error:", errorText);
    return null;
  }
  const text = result.content?.find(c => c.type === "text")?.text;
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// Handle both formats
const data = extractData<any>(result);
const items = data?.response || data || [];
```

### 5. Event Propagation

```typescript
// Stop propagation at multiple levels
<div onClick={(e) => e.stopPropagation()}>
  <ActionsDropdown /> {/* Clicks don't bubble to card */}
</div>

// On all nested clickables
<button onClick={(e) => {
  e.stopPropagation();
  handleAction();
}}>
```

### 6. Dynamic Sizing

```typescript
// Request space for modals
useEffect(() => {
  app.notification({
    method: "ui/notifications/size-changed",
    params: { height: 700 }
  }).catch(() => {});

  return () => {
    app.notification({
      method: "ui/notifications/size-changed",
      params: { height: 500 }
    }).catch(() => {});
  };
}, [app]);
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tool validation error | Wrap parameters with model name (`query_model`, `manage_request`) |
| Dark mode not applying | Set `data-theme` attribute on `document.documentElement` |
| Modal opens parent modal | Add `stopPropagation()` on all clickable wrappers |
| Missing field errors | Add fields to Python Pydantic model with defaults |
| CSS class conflicts | Use specific selectors (`.badge.type` not `.type`) |
| Container too small | Request size via `size-changed` notification |
| Urgency vs Priority | Urgency=High/Low, Priority=P1-P5 (different!) |

## File Checklist

**Minimum files needed**:
- ✅ `src/mcp-app.tsx` - Main component
- ✅ `src/api.ts` - Tool calls
- ✅ `src/styles.css` - Styling with dark mode
- ✅ `src/vite-env.d.ts` - TypeScript declarations
- ✅ `src/components/PagerDutyLogo.tsx` - Branding
- ✅ `src/assets/pagerduty-icon.svg` - Official logo
- ✅ `package.json` - Dependencies
- ✅ `tsconfig.json` - TypeScript config
- ✅ `vite.config.ts` - Build config with singlefile plugin
- ✅ Python server integration in `pagerduty_mcp/server.py`

## Skill Usage

```bash
/create-pagerduty-mcp-app <name> [--tools <tools>] [--features <features>]
```

**Skill location**: `.claude/skills/create-pagerduty-mcp-app/`

## Quick Commands

```bash
# Build app
cd mcp-apps/<app-name> && npm run build

# Copy to Python package
cp dist/mcp-app.html ../../pagerduty_mcp/<app_name>_view.html

# Build all apps
cd mcp-apps && ./build-all.sh

# Test Python server
cd .. && uv run pagerduty-mcp --help
```

## Golden Template Stats

- **Build size**: 578KB (152KB gzipped)
- **Components**: 10
- **Tools used**: 13
- **Actions**: 7 functional
- **Load time**: <1s
- **Iterations**: 14

---

**Reference this document** when creating new PagerDuty MCP Apps!
