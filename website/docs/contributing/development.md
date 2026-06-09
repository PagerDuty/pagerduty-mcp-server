---
sidebar_position: 1
---

# Development Setup

This guide covers setting up a local development environment for the PagerDuty MCP Server.

## Prerequisites

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/) package manager
- A PagerDuty account with API access

## Clone the Repository

```bash
git clone https://github.com/PagerDuty/pagerduty-mcp-server.git
cd pagerduty-mcp-server
```

## Install Dependencies

```bash
uv sync --dev
```

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
├── tools/                 # One file per domain (14 domains)
├── models/                # Pydantic models for validation
└── context/               # MCP context management
```
