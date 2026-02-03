build:: build-image
clean-all:: clean-docker
lint:: lint-docker
publish:: publish-image

# OCI Image Annotations https://github.com/opencontainers/image-spec/blob/master/annotations.md
OCI_SOURCE := https://github.com/logdna/$(APP_NAME)
OCI_CREATED := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')

# Default version of Hadolint docker image to use
HADOLINT_VERSION ?= 2.8.0

DOCKER_BUILD_ALWAYS_PULL ?= true
DOCKERFILE_PATH ?= .
DOCKER_IMAGE ?= us.gcr.io/logdna-k8s/$(APP_NAME)
DOCKERFILE ?= $(wildcard $(DOCKERFILE_PATH)/Dockerfile)
DOCKER_BUILD_ARGS ?=
DOCKER_BUILDARG_FLAGS := $(patsubst %, --build-arg %,$(DOCKER_BUILD_ARGS))

# Docker buildx configuration for multi-arch builds
DOCKER_BUILDX ?= $(DOCKER) buildx
DOCKER_PLATFORMS ?= linux/amd64,linux/arm64
BUILDX_BUILDER ?= multiarch-builder
DOCKER_BUILD_MULTIARCH ?= false

ifndef HADOLINT_COMMAND
    HADOLINT_COMMAND := $(DOCKER_RUN) -v $(shell pwd):/workdir:Z -w /workdir hadolint/hadolint:v$(HADOLINT_VERSION) hadolint --ignore SC2086
endif

# Docker Variables
# Build out a full list of tags for the image build
DOCKER_TAGS := $(GIT_SHA1) $(RELEASE_VERSION)
ifeq ("$(GIT_BRANCH)", $(filter "$(GIT_BRANCH)", "master" "main"))
  DOCKER_TAGS := $(DOCKER_TAGS) $(MINOR_VERSION) $(MAJOR_VERSION)
  ifeq ("$(PUBLISH_LATEST)", "true")
    DOCKER_TAGS := $(DOCKER_TAGS) latest
  endif
endif
# This creates a `docker build` cli-compatible list of the tags
DOCKER_BUILD_TAGS := $(addprefix --tag $(DOCKER_IMAGE):,$(DOCKER_TAGS))

# Adjust build behaviors
ifeq ("$(DOCKER_BUILD_ALWAYS_PULL)", "true")
  DOCKER_BUILD_OPTS += --pull
endif
ifeq ("$(DOCKER_BUILD_NO_CACHE)", "true")
  DOCKER_BUILD_OPTS += --no-cache=true
endif

.PHONY:clean-docker
clean-docker:   ## Clean up docker images from current
	-docker images $(APP_NAME):$(BUILD_VERSION) --format "{{.ID}}" | xargs docker rmi -f

.PHONY:lint-docker
lint-docker: $(DOCKERFILE) ## Lint the Dockerfile for issues
ifneq (,$(DOCKERFILE))
	@# only run if DOCKERFILE isn't empty; control repos don't have one
	$(HADOLINT_COMMAND) $(DOCKERFILE)
endif

.PHONY:buildx-setup
buildx-setup:: ## Set up Docker buildx builder for multi-arch builds
	@echo "Setting up Docker buildx builder '$(BUILDX_BUILDER)'..."
	@if ! $(DOCKER_BUILDX) inspect $(BUILDX_BUILDER) >/dev/null 2>&1; then \
		$(DOCKER_BUILDX) create --name $(BUILDX_BUILDER) --use; \
		$(DOCKER_BUILDX) inspect $(BUILDX_BUILDER) --bootstrap; \
	else \
		$(DOCKER_BUILDX) use $(BUILDX_BUILDER); \
	fi
	@echo "Buildx builder '$(BUILDX_BUILDER)' is ready for multi-arch builds"

.PHONY:buildx-info
buildx-info:: ## Show buildx builder information
	@echo "Buildx builders:"
	@$(DOCKER_BUILDX) ls
	@echo ""
	@if $(DOCKER_BUILDX) inspect $(BUILDX_BUILDER) >/dev/null 2>&1; then \
		echo "Current builder '$(BUILDX_BUILDER)' details:"; \
		$(DOCKER_BUILDX) inspect $(BUILDX_BUILDER); \
	fi

.PHONY:publish-image
publish-image:: ## Publish SemVer compliant releases to our internal docker registry
ifneq (,$(DOCKERFILE))
ifeq ("$(DOCKER_BUILD_MULTIARCH)", "true")
	@echo "Building and pushing multi-arch image for platforms: $(DOCKER_PLATFORMS)"
	@$(MAKE) buildx-setup
	@$(DOCKER_BUILDX) build \
		--platform $(DOCKER_PLATFORMS) \
		$(DOCKER_BUILD_OPTS) \
		--build-arg GITHUB_TOKEN \
		--build-arg GITHUB_PACKAGES_TOKEN \
		--build-arg APP_VERSION=$(APP_VERSION) \
		--build-arg BUILD_VERSION=$(BUILD_VERSION) \
		--build-arg GIT_SHA1=$(GIT_SHA1) \
		--build-arg IMAGE_TITLE="$(TITLE)" \
		$(DOCKER_BUILDARG_FLAGS) \
		--build-arg OCI_SOURCE=$(OCI_SOURCE) \
		$(foreach tag,$(DOCKER_TAGS),--tag $(DOCKER_IMAGE):$(tag)) \
		--push \
		--file $(DOCKERFILE) \
		.
	@echo "Successfully pushed multi-arch image $(DOCKER_IMAGE) with tags: $(DOCKER_TAGS)"
else
	@$(MAKE) build-image
	@for version in $(DOCKER_TAGS); do \
		$(DOCKER) push $(DOCKER_IMAGE):$${version}; \
	done
endif
endif

.PHONY:build-image
build-image:: $(BUILD_ENV) ## Build a docker image as specified in the Dockerfile
ifneq (,$(DOCKERFILE))
	@# only run if DOCKERFILE isn't empty; control repos don't have one
	@$(DOCKER) build --load . -f $(DOCKERFILE) \
		$(DOCKER_BUILD_TAGS) \
		$(DOCKER_BUILD_OPTS) \
		--build-arg GITHUB_TOKEN \
		--build-arg GITHUB_PACKAGES_TOKEN \
		--build-arg APP_VERSION=$(APP_VERSION) \
		--build-arg BUILD_VERSION=$(BUILD_VERSION) \
		--build-arg GIT_SHA1=$(GIT_SHA1) \
		--build-arg IMAGE_TITLE="$(TITLE)" \
		$(DOCKER_BUILDARG_FLAGS) \
		--build-arg OCI_SOURCE=$(OCI_SOURCE)
endif
