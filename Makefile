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

ensure-namespace:
	@test -n "$$QUAY_NAMESPACE" || (echo "Error: QUAY_NAMESPACE is required to push quay.io" && exit 1)

.PHONY: build
build: ## Build the container image
	@echo "Building container image..."
	$(CONTAINER_RUNTIME) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f Dockerfile.dev --arch amd64 .

.PHONY: clean
clean: ## Remove container image
	@echo "Cleaning up..."
	$(CONTAINER_RUNTIME) rmi -f $(IMAGE_NAME):$(IMAGE_TAG) || true

.PHONY: push
push: ensure-namespace build ## Tag and push container image to Quay.io
	@echo "Tagging and pushing to quay.io/$(QUAY_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)..."
	$(CONTAINER_RUNTIME) tag $(IMAGE_NAME):$(IMAGE_TAG) quay.io/$(QUAY_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)
	$(CONTAINER_RUNTIME) push quay.io/$(QUAY_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

# -------------------------------------
# Dependencies
# -------------------------------------

.PHONY: requirements
requirements: ## Generate requirements.txt files from pyproject.toml
	pip-compile -o requirements/requirements.txt pyproject.toml
	pip-compile --extra dev --extra test -o requirements/requirements-dev.txt pyproject.toml
	pip-compile --extra test -o requirements/requirements-test.txt pyproject.toml
