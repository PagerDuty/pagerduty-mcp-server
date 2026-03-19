---
sidebar_position: 3
---

# Authentication

The PagerDuty MCP Server authenticates using a **PagerDuty User API Token**.

## Creating an API Token

1. Log in to [PagerDuty](https://app.pagerduty.com)
2. Click your avatar in the top-right → **My Profile**
3. Select the **User Settings** tab
4. Scroll to **API Access** → **Create New API User Token**
5. Give the token a name (e.g., `mcp-server`) and click **Create Token**
6. Copy the token immediately — it will not be shown again

## Setting the Token

### Environment Variable (Recommended)

Set `PAGERDUTY_USER_API_KEY` in your environment or MCP client configuration:

```bash
export PAGERDUTY_USER_API_KEY="your-token-here"
```

### Per-Client Configuration

Most MCP clients allow setting environment variables in their config. See the [Installation guides](../installation/cursor) for client-specific examples.

## EU Region

If your PagerDuty account is on the EU region, also set:

```bash
export PAGERDUTY_API_HOST="https://api.eu.pagerduty.com"
```

## Security Best Practices

- Never hardcode tokens in configuration files committed to version control
- Use environment variable injection (e.g., `$ENV_VAR` references in VS Code settings)
- Rotate tokens periodically via PagerDuty's API Access settings
- Use the minimum required permissions for read-only workflows
