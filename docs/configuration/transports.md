# Transport Modes

The server supports three MCP transports, selected via the `--transport` flag:

| Transport | Use case | Default |
|-----------|----------|---------|
| `stdio` | Local clients launched as a subprocess (Cursor, VS Code). | ✅ |
| `streamable-http` | Long-running remote/server deployments. MCP endpoint at `/mcp`. | |
| `sse` | Legacy Server-Sent Events transport. | |

The default remains `stdio`, so existing local integrations are unaffected.

For HTTP-based transports, `--host` (default `127.0.0.1`) and `--port` (default `8000`) control the
listen address. These can also be set with the `MCP_HOST` and `MCP_PORT` environment variables — see
[Environment Variables](./environment-variables.md).

> [!WARNING]
> **HTTP transports have no built-in authentication.**
>
> When running `streamable-http` or `sse`, the MCP endpoint is exposed with **no authentication**, and
> every request uses the single `PAGERDUTY_USER_API_KEY` the server was started with. Any client that
> can reach the host/port can invoke tools — including write tools when `--enable-write-tools` is set —
> with that key's full PagerDuty privileges.
>
> - The default bind address is `127.0.0.1` (loopback only) — keep it that way for local use.
> - Only bind to `0.0.0.0` or a routable address when the endpoint sits behind an authenticating
>   reverse proxy / API gateway (e.g. oauth2-proxy, mTLS) or on a trusted network. Do not expose it
>   directly to untrusted networks.

## Running as a remote streamable-HTTP server

```bash
pagerduty-mcp --transport streamable-http --host 0.0.0.0 --port 8000
# MCP endpoint: http://<your-machine-ip>:8000/mcp
# ⚠️ Only use --host 0.0.0.0 behind an authenticating proxy or on a trusted network.
```

Using environment variables instead of flags:

```bash
MCP_HOST=0.0.0.0 MCP_PORT=8000 pagerduty-mcp --transport streamable-http
```

With Docker (using a [locally built image](../installation/docker.md#build-locally)):

```bash
docker run -d -p 8000:8000 \
  -e PAGERDUTY_USER_API_KEY="your-api-key-here" \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  pagerduty-mcp:latest \
  --transport streamable-http
```

> [!NOTE]
> For PagerDuty's own hosted server — no local install, OAuth support — see
> [Remote MCP Server Setup](../remote-server/setup.md).
