# Docker

The PagerDuty MCP Server is available as a Docker image, providing isolation and portability.

## Build Locally

The published image is used in the examples below. To build from a clone of the repository instead:

```bash
docker build -t pagerduty-mcp:latest .
```

Substitute `pagerduty-mcp:latest` for `ghcr.io/pagerduty/pagerduty-mcp:latest` in any command below.

## Run with Docker

```bash
docker run --rm -i \
  -e PAGERDUTY_USER_API_KEY="your-api-token-here" \
  ghcr.io/pagerduty/pagerduty-mcp:latest
```

## Run with Write Tools

```bash
docker run --rm -i \
  -e PAGERDUTY_USER_API_KEY="your-api-token-here" \
  ghcr.io/pagerduty/pagerduty-mcp:latest \
  --enable-write-tools
```

## Docker Compose

Create a `docker-compose.yml`:

```yaml
services:
  pagerduty-mcp:
    image: ghcr.io/pagerduty/pagerduty-mcp:latest
    environment:
      PAGERDUTY_USER_API_KEY: ${PAGERDUTY_USER_API_KEY}
    stdin_open: true
    tty: true
```

## Integrate with MCP Clients

To use the Docker container as your MCP server, configure your client to use Docker as the command:

```json
{
  "mcpServers": {
    "pagerduty": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "PAGERDUTY_USER_API_KEY",
        "ghcr.io/pagerduty/pagerduty-mcp:latest"
      ],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

## EU Region with Docker

```bash
docker run --rm -i \
  -e PAGERDUTY_USER_API_KEY="your-api-token-here" \
  -e PAGERDUTY_API_HOST="https://api.eu.pagerduty.com" \
  ghcr.io/pagerduty/pagerduty-mcp:latest
```
