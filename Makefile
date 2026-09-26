.ONESHELL:
SHELL := /bin/bash

.SILENT:

DEFAULT_GOAL := help
.PHONY: help
help:
	awk 'BEGIN {FS = ":.*?## "} /^[%a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Create poetry environment and install all dependencies.
	poetry config virtualenvs.in-project true --local
	poetry env use 3.12
	poetry install

.PHONY: lock
lock:
	poetry lock --no-update

.PHONY: checks
checks: style-check static-check ## Run all checks.

.PHONY: style-check
style-check: ## Run style checks.
	printf "Style Checking with Ruff\n"
	poetry run ruff check

.PHONY: static-check
static-check: ## Run strict typing checks.
	printf "Static Checking with Mypy\n"
	poetry run mypy .

.PHONY: restyle
restyle: ## Reformat code with ruff.
	poetry run ruff format .
	poetry run ruff check --fix .

.PHONY: tests
tests: ## Run unit + integration tests (fast, no Docker needed).
	PYTHONPATH= poetry run pytest -s

.PHONY: tests-e2e
tests-e2e: ## Run e2e tests against a real docker-compose stack (slow, needs Docker).
	PYTHONPATH= poetry run pytest -s -m e2e tests/e2e