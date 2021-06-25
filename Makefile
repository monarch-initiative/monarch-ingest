MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

.DEFAULT_GOAL := all
SHELL := bash

.PHONY: all
all: install-poetry format test

.PHONY: install-poetry
install-poetry:
	pip install poetry

install-requirements: install-poetry
	poetry install

.PHONY: test
test: install-requirements
	poetry run python -m pytest

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist

.PHONY: lint
lint:
	poetry run flake8 --exit-zero --max-line-length 120 mingestibles/ tests/
	poetry run black --check --diff mingestibles tests
	poetry run isort --check-only --diff mingestibles tests

.PHONY: format
format:
	poetry run autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place mingestibles tests
	poetry run isort mingestibles tests
	poetry run black mingestibles tests


