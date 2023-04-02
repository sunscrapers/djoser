.PHONY: init build test migrate runserver run-hooks docs update-deps

init:
	poetry install --all-extras

build:
	poetry run pybabel compile --domain django --directory djoser/locale -f
	poetry build

test:
	poetry run py.test --capture=no --cov-report term-missing --cov-report html --cov=djoser testproject/

migrate:
	poetry run python testproject/manage.py migrate

runserver:
	poetry run python testproject/manage.py runserver

run-hooks:
	poetry install --only code-quality
	pre-commit run --all-files --show-diff-on-failure

docs:
	poetry config virtualenvs.create false
	poetry install --only docs
	cd docs && make html

update-deps:
	poetry update
