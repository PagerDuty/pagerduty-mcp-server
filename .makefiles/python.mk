lint:: lint-python
setup:: setup-python
test:: test-pytest
version:: version-python

REPORTSDIR ?= ./reports
SEMANTIC_RELEASE_CONFIG ?= pyproject.toml

# Use uv for Python tooling
UV ?= uv

# For non-release branches, just print what version would be released (dry-run)
# For release branches, run the full publish workflow
PYTHON_SEMANTIC_RELEASE_SUBCOMMAND := publish
ifneq ($(GIT_BRANCH), $(filter main master, $(GIT_BRANCH)))
    PYTHON_SEMANTIC_RELEASE_SUBCOMMAND := version --print
endif

export

# Add linters and formatters
lint-python:: lint-ruff lint-mypy

clean::
	rm -rf .venv .pytest_cache __pycache__

$(REPORTSDIR):
	@mkdir -p $(@)

.PHONY:format
format: setup-python      ## Format code using ruff
	$(UV) run ruff format .

.PHONY:lint-mypy
lint-mypy: setup-python ## Run type checking with mypy
	$(UV) run mypy pagerduty_mcp/

.PHONY:lint-ruff
lint-ruff: setup-python ## Run linting with ruff
	$(UV) run ruff check .

.PHONY:setup-python
setup-python: ## Install dependencies using uv
	$(UV) sync --group dev

.PHONY:test-pytest
test-pytest: setup-python | $(REPORTSDIR)  ## Run pytest suite
	$(UV) run pytest tests/ \
		--ignore=tests/evals/ \
		--cov=pagerduty_mcp \
		--cov-report=xml:$(REPORTSDIR)/coverage.xml \
		--cov-report=term \
		--cov-branch \
		-o junit_family=xunit2 \
		--junitxml=$(REPORTSDIR)/pytest.junit.xml

.PHONY:version-python
version-python: ## Automatic version increases using python-semantic-release
ifneq (,$(wildcard $(SEMANTIC_RELEASE_CONFIG)))
	$(UV) run semantic-release $(PYTHON_SEMANTIC_RELEASE_SUBCOMMAND)
endif
