SHELL := /usr/bin/env bash
POETRY ?= poetry
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show the help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: format
format: ## Format code with ruff
	$(POETRY) run ruff check --fix
	$(POETRY) run ruff format

.PHONY: lint
lint: ## Run linting checks (ruff, flake8)
	$(POETRY) run ruff check --exit-non-zero-on-fix
	$(POETRY) run ruff format --check --diff
	$(POETRY) run flake8 .

.PHONY: type-check
type-check: ## Run type checking (mypy)
	$(POETRY) run mypy --enable-error-code=unused-awaitable returns
	$(POETRY) run mypy docs tests

.PHONY: unit
unit: ## Run unit tests with pytest
	$(POETRY) run pytest returns docs/pages tests

.PHONY: typesafety
typesafety: ## Run type-safety tests with pytest-mypy-plugins
	$(POETRY) run pytest typesafety -p no:cov -o addopts=""

.PHONY: slots
slots: ## Check __slots__ correctness with slotscheck
	$(POETRY) run python -m slotscheck returns --verbose

.PHONY: package
package: ## Check package dependencies with pip
	$(POETRY) run pip check

.PHONY: test
test: lint type-check unit slots package ## Run all checks (lint, type-check, unit, slots, package)
