.PHONY: init build test migrate runserver run-hooks docs update-deps

init:
	uv sync --all-extras --all-groups

build:
	uv run --group test pybabel compile --domain django --directory djoser/locale -f
	uv build

test:
	uv run py.test --capture=no --cov-report term-missing --cov-report html --cov=djoser testproject/
	uv run coverage xml

migrate:
	uv run python testproject/manage.py migrate

runserver:
	uv run python testproject/manage.py runserver

run-hooks:
	uv run pre-commit run --all-files --show-diff-on-failure

docs:
	uv sync --group docs --inexact
	cd docs && $(MAKE) html SPHINXBUILD="uv run python -msphinx"

update-deps:
	uv lock --upgrade
