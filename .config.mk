APP_VERSION := $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
APP_NAME = pagerduty-mcp
DOCKERFILE_PATH = .
PUBLISH_LATEST=true

# Docker build configuration
DOCKER_BUILD_MULTIARCH = true
DOCKER_IMAGE = us.gcr.io/logdna-k8s/pagerduty-mcp
OCI_SOURCE = https://github.com/logdna/pagerduty-mcp-server

# Python test configuration
PYTEST_REQUIREMENTS = ".[dev]"

# Enable semantic release
SEMANTIC_RELEASE_CONFIG=pyproject.toml
UPSTREAM_VERSION=0.12.0
