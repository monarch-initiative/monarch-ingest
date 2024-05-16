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

RUN = poetry run

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
	$(RUN) python -m pytest tests


.PHONY: docs
docs: install-full
	$(RUN) typer src/monarch_ingest/main.py utils docs --name ingest --output docs/CLI.md
	

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist


.PHONY: lint
lint: install-full
	$(RUN) ruff check --diff --exit-zero src/ tests/
	$(RUN) black --check --diff -l 120 src/ tests/


.PHONY: format
format: install-full
	$(RUN) ruff check --fix --exit-zero src/ tests/
	$(RUN) black -l 120 src/ tests/
