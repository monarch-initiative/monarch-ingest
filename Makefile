MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

.DEFAULT_GOAL := all
SHELL := bash

.PHONY: all
all: install-requirements format test

.PHONY: install-poetry
install-poetry:
	pip install poetry

install-requirements: install-poetry
	poetry install

.PHONY: test
test: 
	poetry run python -m pytest --ignore=source_template

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist

.PHONY: lint
lint:
	poetry run flake8 --exit-zero --max-line-length 120 monarch_ingest/ tests/
	poetry run black --check --diff monarch_ingest tests
	poetry run isort --check-only --diff monarch_ingest tests

.PHONY: format
format:
	poetry run autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place monarch_ingest tests
	poetry run isort monarch_ingest tests
	poetry run black monarch_ingest tests


.PHONY: download
download:
	gsutil -m cp -R gs://monarch-ingest/data .


.PHONY: transform
transform:
	 find monarch_ingest -name "*.yaml" | grep -v "metadata.yaml" | xargs -L 1 poetry run koza transform --global-table monarch_ingest/translation_table.yaml --source 

.PHONY: merge
merge:
	poetry run kgx merge --merge-config merge.yaml

.PHONY:
generate-pipeline:
	poetry run python generate_pipeline.py > pipeline.py

