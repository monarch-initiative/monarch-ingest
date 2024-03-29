MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

WGET = /usr/bin/env wget --timestamping --no-verbose

.DEFAULT_GOAL := all
SHELL := bash


.PHONY: all
all: install format test clean


.PHONY: install
install:
	poetry install


.PHONY: install-full
install-full:
	poetry install --with dev
	

.PHONY: test
test: install
	poetry run python -m pytest tests


.PHONY: docs
docs: install-full
	poetry run typer src/monarch_ingest/main.py utils docs --name ingest --output docs/CLI.md
	

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist


.PHONY: lint
lint: install-full
	poetry run flake8 --exit-zero --max-line-length 120 src/monarch_ingest/ tests/
	poetry run black --check --diff monarch_ingest tests
	poetry run isort --check-only --diff monarch_ingest tests


.PHONY: format
format: install-full
	poetry run autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place monarch_ingest tests
	poetry run isort monarch_ingest tests
	poetry run black monarch_ingest tests
