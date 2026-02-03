# Based on https://github.com/answerbook/repo-template-base

-include .config.mk

# Provide standard defaults - set overrides in .config.mk
SHELL=/bin/bash -o pipefail
ALWAYS_TIMESTAMP_VERSION ?= false
ifndef APP_NAME
    APP_NAME := $(shell git remote -v | awk '/origin/ && /fetch/ { sub(/\.git/, ""); n=split($$2, origin, "/"); print origin[n]}')
endif
PUBLISH_LATEST ?= false
RELEASE_BRANCHES ?= master main

## Define sources for rendering and templating
GIT_SHA1 := $(shell git log --pretty=format:'%h' -n 1)
GIT_BRANCH := $(shell git branch --show-current)
GIT_URL := $(shell git remote get-url origin)
GIT_INFO ?= $(TMP_DIR)/.git-info.$(GIT_SHA1)
ifndef BUILD_URL
    BUILD_URL := localbuild://${USER}@$(shell uname -n | sed "s/'//g")
endif
BUILD_DATESTAMP := $(shell date -u '+%Y%m%dT%H%M%SZ')

TMP_DIR ?= tmp
BUILD_ENV ?= $(TMP_DIR)/build-env
VERSION_INFO ?= $(TMP_DIR)/version-info

# Define commands via docker
DOCKER ?= docker
DOCKER_RUN ?= $(DOCKER) run --rm -i
DOCKER_RUN_BUILD_ENV ?= $(DOCKER_RUN) --env-file=$(BUILD_ENV)

# Handle versioning
ifeq ("$(VERSION_INFO)", "$(wildcard $(VERSION_INFO))")
  # if tmp/build-env exists on disk, use it
  include $(VERSION_INFO)
else ifneq "$(APP_VERSION)" ""
  MAJOR_VERSION := $(shell echo $(APP_VERSION) | sed 's/v//' | cut -f1 -d'.')
  MINOR_VERSION := $(shell echo $(APP_VERSION) | sed 's/v//' | cut -f1-2 -d'.')
  PATCH_VERSION := $(shell echo $(APP_VERSION) | sed 's/v//')
  BUILD_VERSION := $(PATCH_VERSION)-$(BUILD_DATESTAMP)
  ifneq ($(GIT_BRANCH), $(filter $(RELEASE_BRANCHES), $(GIT_BRANCH)))
    RELEASE_VERSION := $(BUILD_VERSION)
  else ifeq ("$(ALWAYS_TIMESTAMP_VERSION)", "true")
    RELEASE_VERSION := $(BUILD_VERSION)
  else
    RELEASE_VERSION := $(PATCH_VERSION)
  endif
else
  BUILD_VERSION = $(BUILD_DATESTAMP)
  RELEASE_VERSION := $(BUILD_VERSION)
endif

# Exports the variables for shell use
export

# Source in repository specific environment variables
MAKEFILE_LIB=.makefiles
MAKEFILE_INCLUDES=$(wildcard $(MAKEFILE_LIB)/*.mk)
include $(MAKEFILE_INCLUDES)

$(BUILD_ENV):: $(GIT_INFO) $(VERSION_INFO)
	@cat $(VERSION_INFO) $(GIT_INFO) | sort > $(@)

$(VERSION_INFO):: $(GIT_INFO)
	@env | awk '!/TOKEN/ && /^(BUILD|APP_NAME)/ || /(VERSION=)/ { print }' | sort > $(@)

$(GIT_INFO):: $(TMP_DIR)
	@env | awk '!/TOKEN/ && /^(GIT)/ { print }' | sort > $(@)

$(TMP_DIR)::
	@mkdir -p $(@)

# This helper function makes debugging much easier.
.PHONY:debug-%
debug-%:              ## Debug a variable by calling `make debug-VARIABLE`
	@echo $(*) = $($(*))

.PHONY:help
.SILENT:help
help:                 ## Show this help, includes list of all actions.
	@awk 'BEGIN {FS = ":.*?## "}; /^.+: .*?## / && !/awk/ {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' ${MAKEFILE_LIST} | sort

.PHONY:build
build:: $(BUILD_ENV)

.PHONY:clean
clean::          ## Cleanup the local checkout
	-rm -rf *.backup tmp/ reports/

.PHONY:clean-all
clean-all:: clean      ## Full cleanup of all artifacts
	-git clean -Xdf

.PHONY:lint
lint:: ## Run all "lint-%" tasks

.PHONY:publish
publish:: ## Run all "publish-%" tasks

.PHONY:setup
setup:: ## Run all "setup-%" tasks (for use in CI)

.PHONY:test
test:: ## Run all "test-%" tasks

.PHONY:version
version:: ## Run all "version-%" tasks

# Local development helpers
.PHONY:run
run: setup-python ## Run the MCP server locally (stdio mode)
	uv run pagerduty-mcp

.PHONY:run-http
run-http: setup-python ## Run the MCP server locally (HTTP mode)
	uv run pagerduty-mcp --transport streamable-http --host 0.0.0.0 --port 8000

.PHONY:debug
debug: setup-python ## Start MCP inspector debugging session
	npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp --enable-write-tools
