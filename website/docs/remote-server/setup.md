---
sidebar_position: 1
---

# Remote MCP Server Setup

The **PagerDuty Remote MCP Server** is a PagerDuty-hosted service that lets you connect your AI assistant to PagerDuty without installing anything locally. 

It supports both OAuth and API keys for authentication (including OAuth metadata discovery), making it easy to set up across teams and enterprise environments.

:::info API Reference
Explore the PagerDuty MCP API specification on the [PagerDuty Developer Portal]((https://developer.pagerduty.com/api-reference/83ebf88243817-mcp-endpoint).
:::

## Prerequisites

- A PagerDuty account
- A PagerDuty [API key][api-key] or [OAuth client][pd-oauth]
- An MCP-compatible client that supports remote/HTTP-based MCP servers (Cursor, VS Code, etc.)

  [api-key]: https://support.pagerduty.com/main/docs/api-access-keys

## How It Works

Unlike the local server that runs as a subprocess on your machine, the remote server:

- Is hosted and maintained by PagerDuty
- Exposes tools via a remote HTTP endpoint
- Requires no local Python installation or `uvx`

## Setup Steps

### Authorization

Generally, both user and account-level credentials are supported, although some tools and filters require user-level authentication (for example, to scope `list_incidents` by `teams` or `assigned`).

To authorize via an API token, provide a custom header: `Authorization: Token token=<your-api-key-here>`

To authorize via OAuth, there are two broad options: 
 - provide static client credentials for [OAuth metadata discovery][omd]
 - provide a token directly via a custom header: `Authorization: Bearer <your-bearer-token-here>` (for example, to use an [App OAuth Token][app-token] obtained via `client-credentials` grant.)

PagerDuty does not currently support Dynamic Client Registration (DCR).

Read more about creating OAuth clients for your PagerDuty account [here][pd-oauth].

  [omd]: https://modelcontextprotocol.io/specification/draft/basic/authorization#authorization-server-discovery
  [pd-oauth]: https://developer.pagerduty.com/docs/oauth-functionality
  [app-token]: https://developer.pagerduty.com/docs/app-oauth-token

### Configure Your MCP Client
  
#### Cursor

Add to `~/.cursor/mcp.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pagerduty": {
      "url": "https://mcp.pagerduty.com/mcp"
    }
  }
}
```

#### Visual Studio Code

Add to `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "pagerduty": {
        "type": "http",
        "url": "https://mcp.pagerduty.com/mcp",
        // for OAuth, leave the headers section commented out or delete it
        //   you will be prompted for client credentials when starting the server
        // uncomment to be prompted for an API key
		// 	"headers": {
		// 		"Authorization": "Token token=${input:pagerduty-api-key}"
		// 	}
      }
    }
  },
	"inputs": [
		{
			"type": "promptString",
			"id": "pagerduty-api-key",
			"description": "PagerDuty API Key",
			"password": true
		},
  }
}
```

For OAuth, leave the headers section commented out or delete it -- Visual Studio Code will prompt you for the OAuth credentials, and provide the necessary redirect URIs.

#### Claude

For OAuth metadata discovery, you'll need to use a static port in the redirect URL (for example, http://localhost:8080/callback), then provide that during configuration:

```
MCP_CLIENT_SECRET=YOUR_CLIENT_SECRET claude mcp add-json pagerduty '{"type":"http","url":"https://mcp.pagerduty.com/mcp","oauth":{"clientId":"YOUR_CLIENT_ID","callbackPort":8080}}' --client-secret
```

For an API key:

```
PAGERDUTY_API_KEY=YOUR_API_KEY claude mcp add-json pagerduty '{"type":"http","url":"https://mcp.pagerduty.com/mcp","headers":{"Authorization":"Token token=${PAGERDUTY_API_KEY}"}}'"
```

## Comparison: Remote vs. Local Server

| Feature | Remote Server | Local Server |
|---------|--------------|-------------|
| Installation required | None | Python + uv or Docker |
| Tool filtering | [Via Scoped Oauth][scopes] | Via `mcp-proxy` |
| EU region support | Use `https://mcp.eu.pagerduty.com/mcp` | `PAGERDUTY_API_HOST` env var |

  [scopes]: https://developer.pagerduty.com/docs/oauth-functionality#scoped-oauth

## Limitations

- **Tool filtering** via [`mcp-proxy`](../configuration/tool-filtering) is not directly available for the remote server (the proxy approach requires a local subprocess to intercept), but you can limit which tools will succeed with a [Scoped OAuth client][scopes].

## Troubleshooting

If you cannot connect to the remote server:

1. Verify that authorization is still valid — re-generate a new one. [More details here](https://developer.pagerduty.com/docs/authentication).
2. Check that your MCP client supports remote/HTTP-based MCP connections
3. Consult the [PagerDuty Developer Portal](https://developer.pagerduty.com/api-reference/d71edf8527b5e-pager-duty-mcp-api) for the latest endpoint URLs and requirements
