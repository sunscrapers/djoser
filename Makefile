init:
	poetry install

build:
	poetry run pybabel compile --domain django --directory djoser/locale
	poetry build

test:
	poetry run py.test --capture=no --cov-report term-missing --cov-report html --cov=djoser testproject/

migrate:
	poetry run python testproject/manage.py migrate

runserver:
	poetry run python testproject/manage.py runserver
