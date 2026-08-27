# Development Setup

This guide covers setting up a local development environment for the PagerDuty MCP Server.

## Prerequisites

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/) package manager, available **globally** — the MCP server is
  launched from arbitrary working directories by MCP clients, so `uv` must be on your `PATH`. See the
  [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).
- A PagerDuty account with API access
- Optionally [asdf-vm](https://asdf-vm.com/), to pin the Python/Node/uv versions this repo declares
  in `.tool-versions`

## Clone the Repository

```bash
git clone https://github.com/PagerDuty/pagerduty-mcp-server.git
cd pagerduty-mcp-server
```

## Install Dependencies

If you use `asdf`, install the plugins and the pinned tool versions first:

```bash
asdf plugin add python
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin add uv
asdf install
```

Then create the virtual environment and install dependencies:

```bash
uv sync --dev
```

> [!TIP]
> You may need to restart your terminal and/or your editor for newly installed tool versions to be
> picked up.

## Configure Environment

```bash
cp .env.example .env
# Edit .env and add your PAGERDUTY_USER_API_KEY
```

## Run the Server Locally

```bash
uv run python -m pagerduty_mcp
```

With write tools:

```bash
uv run python -m pagerduty_mcp --enable-write-tools
```

## Point an MCP Client at Your Clone

To run your local clone instead of the published package, use `uv` rather than `uvx` in your client
configuration and point `--directory` at the clone:

```json
"pagerduty-mcp": {
    "type": "stdio",
    "command": "uv",
    "args": [
        "run",
        "--directory",
        "/path/to/your/mcp-server-directory",
        "python",
        "-m",
        "pagerduty_mcp",
        "--enable-write-tools"
    ],
    "env": {
        "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}",
        "PAGERDUTY_API_HOST": "https://api.pagerduty.com"
    }
}
```

Replace `/path/to/your/mcp-server-directory` with the full path to your clone, and set
`PAGERDUTY_API_HOST` to `https://api.eu.pagerduty.com` for EU accounts.

## Development Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all unit tests |
| `make test-coverage` | Run tests with coverage report |
| `make lint` | Run ruff linter |
| `make format` | Auto-format code with ruff |
| `make check` | Run all checks (lint + test-coverage) |
| `make debug` | Start MCP Inspector for debugging |

## Running Tests

```bash
make test
```

## MCP Inspector

The MCP Inspector is a debugging tool for testing MCP servers interactively:

```bash
make debug
```

This starts the inspector at `http://localhost:5173`.

## Project Structure

```
pagerduty_mcp/
├── server.py              # FastMCP server setup
├── tools/                 # One file per domain
├── models/                # Pydantic models for validation
└── context/               # MCP context management
```
