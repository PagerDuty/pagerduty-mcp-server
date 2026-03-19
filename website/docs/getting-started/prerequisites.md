---
sidebar_position: 1
---

# Prerequisites

Before installing the PagerDuty MCP Server, ensure you have the following.

## For Local Server

### Python Runtime

The PagerDuty MCP Server requires Python 3.12. The recommended way to install and run it is via [`uv`](https://docs.astral.sh/uv/), which handles Python version management automatically.

Install `uv`:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

### PagerDuty API Token

You need a **PagerDuty User API Token**:

1. Log in to your PagerDuty account
2. Navigate to **My Profile** → **User Settings** → **API Access**
3. Click **Create New API User Token**
4. Copy the token — you'll need it for authentication

:::caution
Store your API token securely. Never commit it to version control.
:::

## For Remote Server

The remote PagerDuty MCP Server is OAuth-based. You only need:

- A PagerDuty account
- An MCP-compatible client (Cursor, VS Code, Claude Desktop, etc.)

See [Remote Server Setup](../remote-server/setup) for details.

## Supported MCP Clients

| Client | Local Server | Remote Server |
|--------|-------------|---------------|
| Cursor | ✅ | ✅ |
| VS Code | ✅ | ✅ |
| Claude Desktop | ✅ | — |
| Any MCP client | ✅ | — |
