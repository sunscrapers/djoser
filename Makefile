init:
	poetry install -E test

build:
	poetry run pybabel compile --domain django --directory djoser/locale -f
	poetry build

test:
	poetry run py.test --capture=no --cov-report term-missing --cov-report html --cov=djoser testproject/

migrate:
	poetry run python testproject/manage.py migrate

runserver:
	poetry run python testproject/manage.py runserver
