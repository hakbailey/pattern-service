.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@grep -hE '^[a-zA-Z0-9._-]+:.*?##' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}' | \
	sort -u


# -------------------------------------
# Container image
# -------------------------------------

CONTAINER_RUNTIME ?= podman
IMAGE_NAME ?= pattern-service
IMAGE_TAG ?= latest
QUAY_NAMESPACE ?= ansible
BUILD_ARGS ?= "--arch amd64"

ensure-namespace:
	@test -n "$$QUAY_NAMESPACE" || (echo "Error: QUAY_NAMESPACE is required to push quay.io" && exit 1)

.PHONY: build
build: ## Build the container image
	@echo "Building container image..."
	$(CONTAINER_RUNTIME) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f tools/docker/Dockerfile.dev $(BUILD_ARGS) .

.PHONY: clean
clean: ## Remove container image
	@echo "Cleaning up..."
	$(CONTAINER_RUNTIME) rmi -f $(IMAGE_NAME):$(IMAGE_TAG) || true

.PHONY: push
push: ensure-namespace build ## Tag and push container image to Quay.io
	@echo "Tagging and pushing to quay.io/$(QUAY_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)..."
	$(CONTAINER_RUNTIME) tag $(IMAGE_NAME):$(IMAGE_TAG) quay.io/$(QUAY_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)
	$(CONTAINER_RUNTIME) push quay.io/$(QUAY_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

#--------------------------------------
# Compose
# -------------------------------------
.PHONY: compose-build
compose-build:
	$(CONTAINER_RUNTIME) compose -f tools/docker/docker-compose.yaml $(COMPOSE_OPTS) build

.PHONY: compose-up
compose-up:
	$(CONTAINER_RUNTIME) compose -f tools/docker/docker-compose.yaml $(COMPOSE_OPTS) up $(COMPOSE_UP_OPTS) --remove-orphans

.PHONY: compose-down
compose-down:
	$(CONTAINER_RUNTIME) compose -f tools/docker/docker-compose.yaml $(COMPOSE_OPTS) down --remove-orphans

.PHONY: compose-clean
compose-clean:
	$(CONTAINER_RUNTIME) compose -f tools/docker/docker-compose.yaml rm -sf
	docker rmi --force localhost/ansible-pattern-service-api localhost/ansible-pattern-service-worker
	docker volume rm -f postgres_data

.PHONY: compose-restart
compose-restart: compose-down compose-clean compose-up

# -------------------------------------
# Dependencies
# -------------------------------------

.PHONY: requirements
requirements: ## Generate requirements.txt files from pyproject.toml
	pip-compile -o requirements/requirements.txt pyproject.toml
	pip-compile --extra dev --extra test -o requirements/requirements-dev.txt pyproject.toml
	pip-compile --extra test -o requirements/requirements-test.txt pyproject.toml
