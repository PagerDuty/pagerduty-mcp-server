---
sidebar_position: 2
---

# Contributing Guidelines

Thank you for contributing to the PagerDuty MCP Server!

## Getting Started

1. Fork the repository on GitHub
2. Set up your [development environment](./development)
3. Create a feature branch: `git checkout -b feat/my-feature`
4. Make your changes
5. Run tests: `make check`
6. Submit a Pull Request

## Code Standards

### Python Style

- **Formatter:** Ruff (configured in `pyproject.toml`)
- **Line length:** 120 characters
- **Docstrings:** Google style
- **Type hints:** Required on all public functions

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new tool for listing X
fix: correct parameter handling in Y
docs: update README for Z
```

### Adding a New Tool

1. Add the tool function to the appropriate file in `pagerduty_mcp/tools/`
2. Add Pydantic models to `pagerduty_mcp/models/` if needed
3. Register the tool in `pagerduty_mcp/tools/__init__.py` (in `read_tools` or `write_tools`)
4. Add tests in `tests/`

### Tool Annotations

All tools must use `ToolAnnotations`:

```python
# Read-only tool
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
async def list_something(...):
    ...

# Write tool
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
async def create_something(...):
    ...
```

## Pull Request Process

1. Ensure all tests pass: `make check`
2. Update documentation if adding new tools or changing behavior
3. Fill out the pull request template completely
4. Request review from a maintainer

## Code of Conduct

This project follows the [PagerDuty Code of Conduct](https://github.com/PagerDuty/pagerduty-mcp-server/blob/main/CODE_OF_CONDUCT.md).

## Reporting Security Issues

See [SECURITY.md](https://github.com/PagerDuty/pagerduty-mcp-server/blob/main/SECURITY.md) for the vulnerability disclosure policy.
