.PHONY: help test test-coverage test-html-coverage clean install dev-install lint format check

# Default target
help:
	@echo "Available commands:"
	@echo "  test              Run all unit tests"
	@echo "  test-coverage     Run tests with coverage report"
	@echo "  test-html-coverage Run tests with HTML coverage report"
	@echo "  clean             Clean up generated files"
	@echo "  install           Install dependencies"
	@echo "  dev-install       Install development dependencies"
	@echo "  lint              Run linting checks"
	@echo "  format            Format code"
	@echo "  check             Run all checks (lint, format, test)"

# Run all unit tests
test:
	@echo "Running all unit tests..."
	uv run python -m pytest tests/ -v

# Run tests with coverage report
test-coverage:
	@echo "Running tests with coverage..."
	uv run python -m coverage run -m pytest tests/
	@echo "\nCoverage Report:"
	uv run python -m coverage report --include="pagerduty_mcp/tools/*" --show-missing
	@echo "\nDetailed Coverage by Module:"
	@echo "================================"
	uv run python -m coverage report --include="pagerduty_mcp/tools/incidents.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/users.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/services.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/teams.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/schedules.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/escalation_policies.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/oncalls.py" --show-missing
	uv run python -m coverage report --include="pagerduty_mcp/tools/event_orchestrations.py" --show-missing

# Run tests with HTML coverage report
test-html-coverage:
	@echo "Running tests with HTML coverage report..."
	uv run python -m coverage run -m pytest tests/
	uv run python -m coverage html --include="pagerduty_mcp/tools/*"
	@echo "HTML coverage report generated in htmlcov/index.html"

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Install dependencies
install:
	@echo "Installing dependencies..."
	uv sync

# Install development dependencies
dev-install:
	@echo "Installing development dependencies..."
	uv sync --group dev

# Run linting checks
lint:
	@echo "Running linting checks..."
	uv run python -m ruff check .

# Format code
format:
	@echo "Formatting code..."
	uv run python -m ruff format .

# Run all checks
check: lint test-coverage
	@echo "All checks completed!"

# Coverage summary
coverage-summary:
	@echo "Coverage Summary:"
	@echo "================="
	@uv run python -m coverage run -m pytest tests/ > /dev/null 2>&1
	@uv run python -m coverage report --include="pagerduty_mcp/tools/*" | tail -1

# Start mcp server debugging session
debug:
	@echo "Starting mcp server debugging session..."
	npx @modelcontextprotocol/inspector uv run --directory ./ python -m pagerduty_mcp --enable-write-tools
