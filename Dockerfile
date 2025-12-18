# Multi-stage Dockerfile for PagerDuty MCP Server
# Based on uv best practices for Python 3.12

# Stage 1: Builder - Install dependencies and project
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy dependency files and source code
COPY pyproject.toml README.md ./
COPY pagerduty_mcp/ ./pagerduty_mcp/

# Set environment variables for uv optimization
ENV UV_LINK_MODE=copy

# Install project with dependencies
# Using cache mount for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --compile-bytecode

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder (includes installed project)
COPY --from=builder /app/.venv /app/.venv

# Copy application source code (needed for runtime)
COPY pagerduty_mcp/ /app/pagerduty_mcp/

# Create non-root user for security
RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set default PagerDuty API host (can be overridden)
ENV PAGERDUTY_API_HOST="https://api.pagerduty.com"

# Health check to verify the server can start
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pagerduty_mcp" || exit 1

# Entry point for the MCP server (stdio transport)
ENTRYPOINT ["python", "-m", "pagerduty_mcp"]

# Default command (read-only mode)
# To enable write tools, pass: --enable-write-tools
CMD []
